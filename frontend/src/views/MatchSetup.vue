<template>
  <div class="space-y-6 pb-12">
    <div class="text-center">
      <h1 class="text-3xl font-extrabold tracking-tight">Select Match</h1>
      <p class="text-dark-400 mt-2">Choose the IPL season and two franchises to begin the draft</p>
    </div>
    
    <!-- Season Selection -->
    <div class="max-w-xs mx-auto mb-8">
      <label class="block text-sm font-bold text-dark-400 uppercase tracking-widest mb-2 text-center">Season</label>
      <div class="relative">
        <select v-model="selectedSeason" class="w-full appearance-none bg-dark-800 border-2 border-dark-700 text-white font-bold py-3 px-4 rounded-xl focus:outline-none focus:border-brand transition-colors text-center cursor-pointer">
          <option disabled value="">Select Season</option>
          <option v-for="season in seasons" :key="season" :value="season">{{ season }}</option>
        </select>
        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-dark-400">
          <svg class="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
        </div>
      </div>
    </div>

    <!-- Team Selection -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto" :class="!selectedSeason ? 'opacity-50 pointer-events-none grayscale' : ''">
      <div v-for="team in teams" :key="team.id" 
           @click="toggleTeam(team.id)"
           class="aspect-square bg-dark-800 rounded-3xl border-2 cursor-pointer transition-all duration-300 flex flex-col items-center justify-center hover:-translate-y-2 hover:shadow-2xl hover:shadow-brand/20 group overflow-hidden relative"
           :class="selected.includes(team.id) ? 'border-brand bg-dark-700/80 shadow-brand/30 shadow-2xl scale-105' : 'border-dark-700 hover:border-dark-500'">
        
        <div class="absolute inset-0 bg-gradient-to-t from-dark-900/80 to-transparent z-0"></div>
        
        <img :src="team.logo_url" :alt="team.id" class="w-24 h-24 md:w-32 md:h-32 object-contain z-10 transition-transform duration-500 group-hover:scale-110 drop-shadow-2xl" />
        
        <div class="absolute top-2 right-2 w-6 h-6 rounded-full bg-brand flex items-center justify-center transform transition-transform duration-300"
             :class="selected.includes(team.id) ? 'scale-100 opacity-100' : 'scale-0 opacity-0'">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path></svg>
        </div>
      </div>
    </div>

    <div class="flex justify-center mt-12">
      <button 
        @click="proceed"
        :disabled="selected.length !== 2 || !selectedSeason"
        class="px-10 py-4 rounded-full font-black text-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-xl"
        :class="(selected.length === 2 && selectedSeason) ? 'bg-gradient-to-r from-brand to-orange-500 text-white shadow-brand/40 hover:scale-105' : 'bg-dark-800 text-dark-500 border border-dark-700'">
        ENTER DRAFT ARENA
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDraftStore } from '../store/draftStore'

const router = useRouter()
const store = useDraftStore()

interface Team {
  id: string
  name: string
  logo_url: string
}

const teams = ref<Team[]>([])
const seasons = ref<string[]>([])
const selectedSeason = ref<string>('')
const selected = ref<string[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const seasonsRes = await fetch('http://localhost:8000/api/seasons')
    if (seasonsRes.ok) {
      seasons.value = await seasonsRes.json()
      if (seasons.value.length > 0) selectedSeason.value = seasons.value[0]
    }
    
    const teamsRes = await fetch('http://localhost:8000/api/teams')
    if (teamsRes.ok) {
      teams.value = await teamsRes.json()
    }
  } catch (error) {
    console.error("Failed to fetch data:", error)
    // Fallback if backend is down
    seasons.value = ['2023', '2024']
    selectedSeason.value = '2023'
    teams.value = [
      { id: 'CSK', name: 'Chennai Super Kings', logo_url: '/logos/csk.png' },
      { id: 'MI', name: 'Mumbai Indians', logo_url: '/logos/mi.png' }
    ]
  } finally {
    loading.value = false
  }
})

const toggleTeam = (teamId: string) => {
  if (selected.value.includes(teamId)) {
    selected.value = selected.value.filter(t => t !== teamId)
  } else if (selected.value.length < 2) {
    selected.value.push(teamId)
  }
}

const proceed = () => {
  if (selected.value.length === 2 && selectedSeason.value) {
    store.selectMatch(selectedSeason.value, selected.value[0], selected.value[1])
    router.push('/draft')
  }
}
</script>
