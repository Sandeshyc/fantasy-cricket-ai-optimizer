import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useDraftStore = defineStore('draft', () => {
  const selectedSeason = ref('')
  const selectedTeamA = ref('')
  const selectedTeamB = ref('')
  
  const draftedPlayers = ref<any[]>([])

  const totalDrafted = computed(() => draftedPlayers.value.length)
  const isDraftComplete = computed(() => totalDrafted.value === 22)

  function selectMatch(season: string, teamA: string, teamB: string) {
    selectedSeason.value = season
    selectedTeamA.value = teamA
    selectedTeamB.value = teamB
    draftedPlayers.value = [] // Reset drafted players on new match
  }

  function draftPlayer(player: any) {
    if (totalDrafted.value < 22 && !draftedPlayers.value.find(p => p.id === player.id)) {
      draftedPlayers.value.push(player)
    }
  }

  function removePlayer(playerId: string) {
    draftedPlayers.value = draftedPlayers.value.filter(p => p.id !== playerId)
  }

  return {
    selectedSeason,
    selectedTeamA,
    selectedTeamB,
    draftedPlayers,
    totalDrafted,
    isDraftComplete,
    selectMatch,
    draftPlayer,
    removePlayer
  }
})
