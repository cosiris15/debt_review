"""
Interest Calculator Tool

Refactored from universal_debt_calculator_cli.py for use as a LangGraph tool.
Supports: simple interest, LPR floating rate, delayed performance, compound, penalty.
"""

from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict, List, Tuple, Optional, Union, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Set Decimal precision for financial calculations
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP


class CalculationType(str, Enum):
    """Supported calculation types."""
    SIMPLE = "simple"
    LPR = "lpr"
    DELAY = "delay"
    COMPOUND = "compound"
    PENALTY = "penalty"


# Embedded LPR data (2019-2025)
LPR_DATA = [
    ("2025-07-21", 3.00, 3.50),
    ("2025-06-20", 3.00, 3.50),
    ("2025-05-20", 3.00, 3.50),
    ("2025-04-21", 3.10, 3.60),
    ("2025-03-20", 3.10, 3.60),
    ("2025-02-20", 3.10, 3.60),
    ("2025-01-20", 3.10, 3.60),
    ("2024-12-20", 3.10, 3.60),
    ("2024-11-20", 3.10, 3.60),
    ("2024-10-21", 3.10, 3.60),
    ("2024-09-20", 3.35, 3.85),
    ("2024-08-20", 3.35, 3.85),
    ("2024-07-22", 3.35, 3.85),
    ("2024-06-20", 3.45, 3.95),
    ("2024-05-20", 3.45, 3.95),
    ("2024-04-22", 3.45, 3.95),
    ("2024-03-20", 3.45, 3.95),
    ("2024-02-20", 3.45, 3.95),
    ("2024-01-22", 3.45, 4.20),
    ("2023-12-20", 3.45, 4.20),
    ("2023-11-20", 3.45, 4.20),
    ("2023-10-20", 3.45, 4.20),
    ("2023-09-20", 3.45, 4.20),
    ("2023-08-21", 3.45, 4.20),
    ("2023-07-20", 3.55, 4.20),
    ("2023-06-20", 3.55, 4.20),
    ("2023-05-22", 3.65, 4.30),
    ("2023-04-20", 3.65, 4.30),
    ("2023-03-20", 3.65, 4.30),
    ("2023-02-20", 3.65, 4.30),
    ("2023-01-20", 3.65, 4.30),
    ("2022-12-20", 3.65, 4.30),
    ("2022-11-21", 3.65, 4.30),
    ("2022-10-20", 3.65, 4.30),
    ("2022-09-20", 3.65, 4.30),
    ("2022-08-22", 3.65, 4.30),
    ("2022-07-20", 3.70, 4.45),
    ("2022-06-20", 3.70, 4.45),
    ("2022-05-20", 3.70, 4.45),
    ("2022-04-20", 3.70, 4.60),
    ("2022-03-21", 3.70, 4.60),
    ("2022-02-21", 3.70, 4.60),
    ("2022-01-20", 3.70, 4.60),
    ("2021-12-20", 3.80, 4.65),
    ("2021-11-22", 3.85, 4.65),
    ("2021-10-20", 3.85, 4.65),
    ("2021-09-22", 3.85, 4.65),
    ("2021-08-20", 3.85, 4.65),
    ("2021-07-20", 3.85, 4.65),
    ("2021-06-21", 3.85, 4.65),
    ("2021-05-20", 3.85, 4.65),
    ("2021-04-20", 3.85, 4.65),
    ("2021-03-22", 3.85, 4.65),
    ("2021-02-22", 3.85, 4.65),
    ("2021-01-20", 3.85, 4.65),
    ("2020-12-21", 3.85, 4.65),
    ("2020-11-20", 3.85, 4.65),
    ("2020-10-20", 3.85, 4.65),
    ("2020-09-21", 3.85, 4.65),
    ("2020-08-20", 3.85, 4.65),
    ("2020-07-20", 3.85, 4.65),
    ("2020-06-22", 3.85, 4.65),
    ("2020-05-20", 3.85, 4.65),
    ("2020-04-20", 3.85, 4.65),
    ("2020-03-20", 4.05, 4.75),
    ("2020-02-20", 4.05, 4.75),
    ("2020-01-20", 4.15, 4.80),
    ("2019-12-20", 4.15, 4.80),
    ("2019-11-20", 4.15, 4.80),
    ("2019-10-21", 4.20, 4.85),
    ("2019-09-20", 4.20, 4.85),
    ("2019-08-20", 4.25, 4.85),
]


class InterestCalculator:
    """
    Universal interest calculator for debt review.

    Supports multiple calculation methods required for bankruptcy debt analysis.
    """

    def __init__(self):
        """Initialize calculator with LPR data."""
        self.lpr_rates = {}
        for date_str, rate_1y, rate_5y in LPR_DATA:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            self.lpr_rates[date_obj] = {
                "1y": Decimal(str(rate_1y)),
                "5y": Decimal(str(rate_5y))
            }
        self.lpr_dates = sorted(self.lpr_rates.keys(), reverse=True)

    def _to_decimal(self, value: Union[float, int, str, Decimal]) -> Decimal:
        """Convert value to Decimal safely."""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    def _parse_date(self, date_input: Union[datetime, str]) -> datetime:
        """Parse date from string or datetime."""
        if isinstance(date_input, datetime):
            return date_input
        try:
            return datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            return datetime.strptime(date_input, '%Y/%m/%d')

    def _get_lpr_rate(self, date: datetime, term: str = "1y") -> Decimal:
        """Get LPR rate for a given date."""
        for lpr_date in self.lpr_dates:
            if date >= lpr_date:
                return self.lpr_rates[lpr_date][term]
        # Return earliest rate if date is before all records
        return self.lpr_rates[self.lpr_dates[-1]][term]

    def calculate_simple_interest(
        self,
        principal: float,
        start_date: str,
        end_date: str,
        annual_rate: float
    ) -> Dict[str, Any]:
        """
        Calculate simple interest.

        Formula: Interest = Principal × Rate × Days / 365
        """
        principal_d = self._to_decimal(principal)
        rate_d = self._to_decimal(annual_rate) / 100
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)

        days = (end - start).days
        if days <= 0:
            return {"error": "End date must be after start date"}

        interest = principal_d * rate_d * days / 365
        interest = interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            "calculation_type": "simple",
            "principal": float(principal_d),
            "annual_rate": annual_rate,
            "start_date": start_date,
            "end_date": end_date,
            "days": days,
            "interest": float(interest),
            "total": float(principal_d + interest),
            "formula": f"{principal} × {annual_rate}% × {days}/365 = {float(interest)}"
        }

    def calculate_lpr_interest(
        self,
        principal: float,
        start_date: str,
        end_date: str,
        multiplier: float = 1.0,
        lpr_term: str = "1y"
    ) -> Dict[str, Any]:
        """
        Calculate interest based on floating LPR rate.

        Rate changes with each LPR announcement.
        """
        principal_d = self._to_decimal(principal)
        multiplier_d = self._to_decimal(multiplier)
        start = self._parse_date(start_date)
        end = self._parse_date(end_date)

        if end <= start:
            return {"error": "End date must be after start date"}

        # Calculate interest for each LPR period
        periods = []
        total_interest = Decimal('0')
        current_date = start

        while current_date < end:
            # Find next LPR change date
            next_lpr_date = None
            for lpr_date in self.lpr_dates:
                if lpr_date > current_date and lpr_date < end:
                    next_lpr_date = lpr_date
                    break

            period_end = next_lpr_date if next_lpr_date else end
            days = (period_end - current_date).days

            if days > 0:
                base_rate = self._get_lpr_rate(current_date, lpr_term)
                effective_rate = base_rate * multiplier_d
                period_interest = principal_d * effective_rate / 100 * days / 365
                period_interest = period_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                periods.append({
                    "start": current_date.strftime('%Y-%m-%d'),
                    "end": period_end.strftime('%Y-%m-%d'),
                    "days": days,
                    "lpr_rate": float(base_rate),
                    "effective_rate": float(effective_rate),
                    "interest": float(period_interest)
                })

                total_interest += period_interest

            current_date = period_end

        total_days = (end - start).days

        return {
            "calculation_type": "lpr",
            "principal": float(principal_d),
            "multiplier": multiplier,
            "lpr_term": lpr_term,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "interest": float(total_interest),
            "total": float(principal_d + total_interest),
            "periods": periods
        }

    def calculate_delay_interest(
        self,
        principal: float,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Calculate delayed performance interest (迟延履行利息).

        Rate: 1.75× of loan benchmark rate (now LPR)
        """
        return self.calculate_lpr_interest(
            principal=principal,
            start_date=start_date,
            end_date=end_date,
            multiplier=1.75,
            lpr_term="1y"
        )

    def calculate_penalty_interest(
        self,
        principal: float,
        start_date: str,
        end_date: str,
        annual_rate: float,
        penalty_cap: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate penalty interest with optional cap.

        Penalty interest is capped at 24% annually per judicial interpretation.
        """
        # Apply 24% cap if rate exceeds
        capped_rate = min(annual_rate, 24.0)

        result = self.calculate_simple_interest(
            principal=principal,
            start_date=start_date,
            end_date=end_date,
            annual_rate=capped_rate
        )

        result["calculation_type"] = "penalty"
        result["original_rate"] = annual_rate
        result["capped_rate"] = capped_rate
        result["rate_was_capped"] = annual_rate > 24.0

        # Apply additional penalty cap if specified
        if penalty_cap and result["interest"] > penalty_cap:
            result["interest"] = penalty_cap
            result["total"] = float(self._to_decimal(principal) + self._to_decimal(penalty_cap))
            result["penalty_cap_applied"] = True

        return result

    def calculate(
        self,
        calculation_type: str,
        principal: float,
        start_date: str,
        end_date: str,
        rate: Optional[float] = None,
        multiplier: float = 1.0,
        lpr_term: str = "1y",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Universal calculation entry point.

        Args:
            calculation_type: One of "simple", "lpr", "delay", "compound", "penalty"
            principal: Principal amount
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            rate: Annual rate for simple/penalty calculations
            multiplier: LPR multiplier (default 1.0)
            lpr_term: "1y" or "5y" for LPR calculations

        Returns:
            Calculation result dictionary
        """
        try:
            calc_type = CalculationType(calculation_type.lower())

            if calc_type == CalculationType.SIMPLE:
                if rate is None:
                    return {"error": "Rate is required for simple interest"}
                return self.calculate_simple_interest(principal, start_date, end_date, rate)

            elif calc_type == CalculationType.LPR:
                return self.calculate_lpr_interest(principal, start_date, end_date, multiplier, lpr_term)

            elif calc_type == CalculationType.DELAY:
                return self.calculate_delay_interest(principal, start_date, end_date)

            elif calc_type == CalculationType.PENALTY:
                if rate is None:
                    return {"error": "Rate is required for penalty interest"}
                return self.calculate_penalty_interest(
                    principal, start_date, end_date, rate,
                    penalty_cap=kwargs.get("penalty_cap")
                )

            elif calc_type == CalculationType.COMPOUND:
                # Compound interest calculation (simplified)
                if rate is None:
                    return {"error": "Rate is required for compound interest"}
                # For now, treat as simple interest
                # TODO: Implement proper compound interest
                return self.calculate_simple_interest(principal, start_date, end_date, rate)

        except ValueError as e:
            return {"error": f"Invalid calculation type: {calculation_type}"}
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return {"error": str(e)}


# Singleton instance
_calculator = None


def get_calculator() -> InterestCalculator:
    """Get or create calculator instance."""
    global _calculator
    if _calculator is None:
        _calculator = InterestCalculator()
    return _calculator


def calculate_interest(
    calculation_type: str,
    principal: float,
    start_date: str,
    end_date: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for calculating interest.

    This is the main entry point for the calculator tool.
    """
    calculator = get_calculator()
    return calculator.calculate(
        calculation_type=calculation_type,
        principal=principal,
        start_date=start_date,
        end_date=end_date,
        **kwargs
    )
