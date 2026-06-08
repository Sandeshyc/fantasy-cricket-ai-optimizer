<template>
  <div class="relative flex flex-col items-center justify-center w-16 md:w-20 group cursor-pointer" @click="$emit('click', player)">
    
    <!-- Player Badge (C/VC) -->
    <div v-if="player.is_captain" class="absolute -top-3 -right-2 bg-gradient-to-br from-yellow-400 to-orange-600 text-white text-[10px] font-black px-2 py-0.5 rounded-full z-30 shadow-lg shadow-orange-500/50 border border-yellow-300">C</div>
    <div v-if="player.is_vice_captain" class="absolute -top-3 -right-2 bg-gradient-to-br from-blue-400 to-blue-700 text-white text-[10px] font-black px-2 py-0.5 rounded-full z-30 shadow-lg shadow-blue-500/50 border border-blue-300">VC</div>

    <!-- Avatar Icon -->
    <div class="w-14 h-14 md:w-16 md:h-16 rounded-full bg-dark-800 flex items-center justify-center shadow-2xl border-4 transition-all duration-300 group-hover:scale-110 group-hover:z-20 relative overflow-hidden"
         :class="player.team === 'CSK' ? 'border-yellow-500 shadow-yellow-500/30' : (player.team === 'MI' ? 'border-blue-500 shadow-blue-500/30' : 'border-brand shadow-brand/30')">
       
       <img :src="player.image" class="w-full h-full object-cover" onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/User_icon_2.svg/2048px-User_icon_2.svg.png'" />
       
       <!-- Credits Overlay -->
       <div class="absolute bottom-0 inset-x-0 bg-dark-900/80 backdrop-blur-sm text-[8px] font-bold text-center py-0.5 text-gray-300">
         {{ player.credits }} CR
       </div>
    </div>

    <!-- Player Name Panel -->
    <div class="mt-2 bg-dark-900/95 px-2 py-1.5 rounded-lg text-center min-w-[75px] backdrop-blur-md shadow-xl border border-dark-700 transition-transform duration-300 group-hover:-translate-y-1">
      <div class="text-white text-[10px] md:text-xs font-bold leading-tight truncate w-full">{{ player.name.split(' ').pop() || player.name }}</div>
      <div class="text-green-400 text-[10px] font-black mt-0.5 drop-shadow-[0_0_2px_rgba(74,222,128,0.8)]">
        {{ (player.predicted_points * (player.is_captain ? 2 : (player.is_vice_captain ? 1.5 : 1))).toFixed(1) }} pts
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  player: any
}>()

defineEmits(['click'])
</script>
