/**
 * Project Store - Manages project and creditor data
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectsApi, creditorsApi } from '@/api/client'
import type { Project, ProjectCreate, Creditor, CreditorCreate } from '@/types'

export const useProjectStore = defineStore('project', () => {
  // State
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const creditors = ref<Creditor[]>([])
  const selectedCreditors = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const creditorsByBatch = computed(() => {
    const batches: Record<number, Creditor[]> = {}
    creditors.value.forEach(c => {
      if (!batches[c.batch_number]) {
        batches[c.batch_number] = []
      }
      batches[c.batch_number].push(c)
    })
    return batches
  })

  const batchNumbers = computed(() =>
    Object.keys(creditorsByBatch.value).map(Number).sort((a, b) => a - b)
  )

  const completedCreditors = computed(() =>
    creditors.value.filter(c => c.status === 'completed').length
  )

  const pendingCreditors = computed(() =>
    creditors.value.filter(c => c.status === 'not_started')
  )

  // Actions
  async function fetchProjects(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      projects.value = await projectsApi.list()
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function fetchProject(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentProject.value = await projectsApi.get(id)
      await fetchCreditors(id)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function createProject(data: ProjectCreate): Promise<Project> {
    loading.value = true
    error.value = null
    try {
      const project = await projectsApi.create(data)
      projects.value.unshift(project)
      return project
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchCreditors(projectId: string, batchNumber?: number): Promise<void> {
    loading.value = true
    error.value = null
    try {
      creditors.value = await creditorsApi.list(projectId, batchNumber)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function createCreditor(data: CreditorCreate): Promise<Creditor> {
    loading.value = true
    error.value = null
    try {
      const creditor = await creditorsApi.create(data)
      creditors.value.push(creditor)
      return creditor
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      loading.value = false
    }
  }

  function toggleCreditorSelection(id: string): void {
    const index = selectedCreditors.value.indexOf(id)
    if (index === -1) {
      selectedCreditors.value.push(id)
    } else {
      selectedCreditors.value.splice(index, 1)
    }
  }

  function selectAllCreditors(): void {
    selectedCreditors.value = creditors.value.map(c => c.id)
  }

  function selectPendingCreditors(): void {
    selectedCreditors.value = pendingCreditors.value.map(c => c.id)
  }

  function clearSelection(): void {
    selectedCreditors.value = []
  }

  function reset(): void {
    currentProject.value = null
    creditors.value = []
    selectedCreditors.value = []
    error.value = null
  }

  return {
    // State
    projects,
    currentProject,
    creditors,
    selectedCreditors,
    loading,
    error,

    // Computed
    creditorsByBatch,
    batchNumbers,
    completedCreditors,
    pendingCreditors,

    // Actions
    fetchProjects,
    fetchProject,
    createProject,
    fetchCreditors,
    createCreditor,
    toggleCreditorSelection,
    selectAllCreditors,
    selectPendingCreditors,
    clearSelection,
    reset
  }
})
