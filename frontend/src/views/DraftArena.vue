<template>
  <div class="space-y-6 pb-12">
    <div class="flex flex-col md:flex-row justify-between items-center bg-dark-800 p-4 rounded-2xl border border-dark-700 sticky top-20 z-40 backdrop-blur-xl bg-dark-800/80 shadow-2xl gap-4">
      <div class="flex items-center space-x-4">
        <div class="flex -space-x-4">
          <img :src="logoA" class="w-12 h-12 rounded-full border-2 border-dark-800 bg-white object-contain p-1 shadow-lg" onerror="this.src=''" />
          <img :src="logoB" class="w-12 h-12 rounded-full border-2 border-dark-800 bg-white object-contain p-1 shadow-lg" onerror="this.src=''" />
        </div>
        <div>
          <h2 class="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Draft Arena <span class="text-brand ml-2">{{ store.selectedSeason }}</span></h2>
          <p class="text-sm font-bold text-dark-400 uppercase tracking-widest">{{ store.selectedTeamA }} VS {{ store.selectedTeamB }}</p>
        </div>
      </div>
      
      <div class="flex items-center space-x-6">
        <div class="text-right">
          <div class="text-3xl font-black" :class="store.totalDrafted === 22 ? 'text-green-400 drop-shadow-[0_0_8px_rgba(74,222,128,0.5)]' : 'text-brand drop-shadow-[0_0_8px_rgba(255,76,41,0.5)]'">
            {{ store.totalDrafted }}<span class="text-dark-500 text-xl">/22</span>
          </div>
          <div class="text-[10px] text-dark-400 uppercase tracking-widest font-bold">Selected</div>
        </div>
        <button 
          @click="runOptimization"
          :disabled="!store.isDraftComplete || isOptimizing"
          class="px-8 py-3 rounded-xl font-black transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shadow-xl"
          :class="store.isDraftComplete ? 'bg-gradient-to-r from-brand to-orange-500 text-white shadow-brand/40 hover:scale-105 hover:shadow-brand/60 animate-pulse' : 'bg-dark-900 border border-dark-700 text-dark-500'">
          <span v-if="isOptimizing">Analyzing...</span>
          <span v-else>RUN AI OPTIMIZER</span>
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Team A Roster -->
      <div class="bg-dark-800/50 p-6 rounded-3xl border border-dark-700 backdrop-blur-sm">
        <h3 class="text-xl font-black mb-6 flex flex-col border-b border-dark-700 pb-4">
          <div class="flex justify-between items-center w-full">
            <span class="flex items-center space-x-3">
               <img :src="logoA" class="w-8 h-8 object-contain bg-white rounded-full p-1" onerror="this.src=''" />
               <span>{{ store.selectedTeamA }}</span>
            </span>
            <span class="text-sm font-bold bg-dark-900 px-3 py-1 rounded-full text-brand border border-dark-700">{{ teamADraftedCount }} / 11</span>
          </div>
          <div v-if="teamAForeignCount >= 4" class="text-xs text-orange-400 mt-3 font-bold flex items-center bg-orange-500/10 py-1.5 px-3 rounded-lg border border-orange-500/20 w-fit">
            <span class="mr-2">⚠️</span> Max 4 overseas players reached. Remaining disabled.
          </div>
        </h3>
        <div class="space-y-3">
          <div v-for="player in teamA_roster" :key="player.id"
               @click="!isDisabled(player) && toggleDraft(player)"
               class="p-3 rounded-2xl border-2 transition-all duration-300 flex justify-between items-center group relative overflow-hidden"
               :class="[
                 isDrafted(player.id) ? 'bg-brand/10 border-brand shadow-[0_0_15px_rgba(255,76,41,0.2)]' : 'bg-dark-900 border-dark-700',
                 isDisabled(player) ? 'opacity-40 grayscale cursor-not-allowed' : 'cursor-pointer hover:border-dark-500 hover:bg-dark-800'
               ]">
            
            <div class="absolute inset-0 bg-gradient-to-r from-brand/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            
            <div class="flex items-center space-x-4 z-10">
              <img :src="player.image" class="w-12 h-12 rounded-full object-cover border-2 border-dark-700" :class="isDrafted(player.id) ? 'border-brand' : ''" onerror="this.src='https://ui-avatars.com/api/?name=Player&background=random'" />
              <div>
                <div class="font-bold text-white text-lg leading-tight">{{ player.name }}</div>
                <div class="flex items-center space-x-2 mt-1">
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-sm uppercase"
                        :class="getRoleColor(player.role)">{{ player.role }}</span>
                  <span v-if="player.is_foreign" title="Overseas Player" class="text-[14px] cursor-help hover:scale-110 transition-transform">✈️</span>
                </div>
              </div>
            </div>
            <div class="z-10 flex items-center space-x-4">
              <div class="font-mono bg-dark-950 px-3 py-1.5 rounded-lg text-sm font-bold border border-dark-700 text-gray-300 shadow-inner">
                {{ player.credits }} CR
              </div>
              <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors"
                   :class="isDrafted(player.id) ? 'bg-brand border-brand' : 'border-dark-600 group-hover:border-dark-400'">
                 <svg v-if="isDrafted(player.id)" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Team B Roster -->
      <div class="bg-dark-800/50 p-6 rounded-3xl border border-dark-700 backdrop-blur-sm">
        <h3 class="text-xl font-black mb-6 flex flex-col border-b border-dark-700 pb-4">
          <div class="flex justify-between items-center w-full">
            <span class="flex items-center space-x-3">
               <img :src="logoB" class="w-8 h-8 object-contain bg-white rounded-full p-1" onerror="this.src=''" />
               <span>{{ store.selectedTeamB }}</span>
            </span>
            <span class="text-sm font-bold bg-dark-900 px-3 py-1 rounded-full text-brand border border-dark-700">{{ teamBDraftedCount }} / 11</span>
          </div>
          <div v-if="teamBForeignCount >= 4" class="text-xs text-orange-400 mt-3 font-bold flex items-center bg-orange-500/10 py-1.5 px-3 rounded-lg border border-orange-500/20 w-fit">
            <span class="mr-2">⚠️</span> Max 4 overseas players reached. Remaining disabled.
          </div>
        </h3>
        <div class="space-y-3">
          <div v-for="player in teamB_roster" :key="player.id"
               @click="!isDisabled(player) && toggleDraft(player)"
               class="p-3 rounded-2xl border-2 transition-all duration-300 flex justify-between items-center group relative overflow-hidden"
               :class="[
                 isDrafted(player.id) ? 'bg-brand/10 border-brand shadow-[0_0_15px_rgba(255,76,41,0.2)]' : 'bg-dark-900 border-dark-700',
                 isDisabled(player) ? 'opacity-40 grayscale cursor-not-allowed' : 'cursor-pointer hover:border-dark-500 hover:bg-dark-800'
               ]">
            
            <div class="absolute inset-0 bg-gradient-to-r from-brand/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            
            <div class="flex items-center space-x-4 z-10">
              <img :src="player.image" class="w-12 h-12 rounded-full object-cover border-2 border-dark-700" :class="isDrafted(player.id) ? 'border-brand' : ''" onerror="this.src='https://ui-avatars.com/api/?name=Player&background=random'" />
              <div>
                <div class="font-bold text-white text-lg leading-tight">{{ player.name }}</div>
                <div class="flex items-center space-x-2 mt-1">
                  <span class="text-[10px] font-bold px-2 py-0.5 rounded-sm uppercase"
                        :class="getRoleColor(player.role)">{{ player.role }}</span>
                  <span v-if="player.is_foreign" title="Overseas Player" class="text-[14px] cursor-help hover:scale-110 transition-transform">✈️</span>
                </div>
              </div>
            </div>
            <div class="z-10 flex items-center space-x-4">
              <div class="font-mono bg-dark-950 px-3 py-1.5 rounded-lg text-sm font-bold border border-dark-700 text-gray-300 shadow-inner">
                {{ player.credits }} CR
              </div>
              <div class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors"
                   :class="isDrafted(player.id) ? 'bg-brand border-brand' : 'border-dark-600 group-hover:border-dark-400'">
                 <svg v-if="isDrafted(player.id)" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDraftStore } from '../store/draftStore'

const router = useRouter()
const store = useDraftStore()
const isOptimizing = ref(false)

if (!store.selectedTeamA || !store.selectedTeamB) {
  router.push('/')
}

const getRoleColor = (role: string) => {
  switch(role) {
    case 'BAT': return 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
    case 'BOWL': return 'bg-green-500/20 text-green-400 border border-green-500/30'
    case 'AR': return 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
    case 'WK': return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
    default: return 'bg-gray-500/20 text-gray-400'
  }
}

const teamA_roster = ref<any[]>([])
const teamB_roster = ref<any[]>([])

const logoA = ref('')
const logoB = ref('')

const getLogoUrl = (teamId: string, teamsList?: any[]) => {
  if (teamsList) {
    const found = teamsList.find((t: any) => t.id.toUpperCase() === teamId.toUpperCase())
    if (found && found.logo_url) return found.logo_url
  }
  const extension = ['LSG', 'GT'].includes(teamId.toUpperCase()) ? 'svg' : 'png'
  return `/logos/${teamId.toLowerCase()}.${extension}`
}

onMounted(async () => {
  if (!store.selectedSeason || !store.selectedTeamA || !store.selectedTeamB) {
    router.push('/')
    return
  }
  
  logoA.value = getLogoUrl(store.selectedTeamA)
  logoB.value = getLogoUrl(store.selectedTeamB)
  
  try {
    const response = await fetch(`http://localhost:8000/api/rosters/${store.selectedSeason}/${store.selectedTeamA}/${store.selectedTeamB}`)
    if (response.ok) {
      const players = await response.json()
      teamA_roster.value = players.filter((p: any) => p.team === store.selectedTeamA)
      teamB_roster.value = players.filter((p: any) => p.team === store.selectedTeamB)
    }
    
    const teamsRes = await fetch('http://localhost:8000/api/teams')
    if (teamsRes.ok) {
      const teamsList = await teamsRes.json()
      logoA.value = getLogoUrl(store.selectedTeamA, teamsList)
      logoB.value = getLogoUrl(store.selectedTeamB, teamsList)
    }
  } catch (error) {
    console.error("Failed to fetch rosters or team logo mappings", error)
  }
})

const teamADraftedCount = computed(() => store.draftedPlayers.filter(p => p.team === store.selectedTeamA).length)
const teamBDraftedCount = computed(() => store.draftedPlayers.filter(p => p.team === store.selectedTeamB).length)

const teamAForeignCount = computed(() => store.draftedPlayers.filter(p => p.team === store.selectedTeamA && p.is_foreign).length)
const teamBForeignCount = computed(() => store.draftedPlayers.filter(p => p.team === store.selectedTeamB && p.is_foreign).length)

const isDrafted = (id: string) => !!store.draftedPlayers.find(p => p.id === id)

const isDisabled = (player: any) => {
  if (isDrafted(player.id)) return false
  if (player.is_foreign) {
    const foreignCount = player.team === store.selectedTeamA ? teamAForeignCount.value : teamBForeignCount.value
    if (foreignCount >= 4) return true
  }
  return false
}


const toggleDraft = (player: any) => {
  if (isDrafted(player.id)) {
    store.removePlayer(player.id)
  } else {
    if (isDisabled(player)) return

    const teamCount = player.team === store.selectedTeamA ? teamADraftedCount.value : teamBDraftedCount.value
    if (store.totalDrafted < 22 && teamCount < 11) {
      store.draftPlayer(player)
    }
  }
}

const runOptimization = async () => {
  if (!store.isDraftComplete) return
  isOptimizing.value = true
  
  try {
    const response = await fetch('http://localhost:8000/api/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        match_id: `${store.selectedTeamA}_${store.selectedTeamB}`,
        team_a: store.selectedTeamA,
        team_b: store.selectedTeamB,
        playing_twenty_two: store.draftedPlayers
      })
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      alert("❌ Math Engine Error: " + (data.detail || "Cannot form a valid 100-credit squad."))
      return
    }
    
    localStorage.setItem('optimizationResults', JSON.stringify(data))
    router.push('/results')
  } catch (e) {
    console.error("Optimization failed", e)
    alert("Could not reach backend API. Make sure FastAPI is running on port 8000.")
  } finally {
    isOptimizing.value = false
  }
}
</script>
