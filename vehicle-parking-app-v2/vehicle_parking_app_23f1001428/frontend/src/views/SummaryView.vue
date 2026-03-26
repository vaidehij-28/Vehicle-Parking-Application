<script setup>
    import {Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement} from 'chart.js'
    import { Bar } from 'vue-chartjs'
    import { Pie } from 'vue-chartjs'
    import { onMounted } from 'vue'
    import { useSummaryStore } from '@/stores/summarystore.js'
    import { useAuthStore } from '@/stores/authstore.js';
    import { useMessageStore } from '@/stores/messagestore.js';

    ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend)
   
    const summaryStore = useSummaryStore()
    const auth_store = useAuthStore();
    const message_store = useMessageStore();
    onMounted(() => {
        summaryStore.fetchSummary()
    })
    async function exportdatatocsv(){
        const reserverres = await fetch("http://127.0.0.1:5000/api/generate_csv", {
      })
      if (!reserverres.ok) {
        throw new Error('failed while fetching reservation details')
      }      
      const data = await reserverres.json()
      message_store.updateErrorMsgs("Data exported to csv and e-mailed");  
    }
</script>

<template>
  <div class="container mt-3">
    <div v-if="summaryStore.loading" class="text-center mt-4">
      <p>Loading summary data...</p>
    </div>
    <div v-else-if="summaryStore.error" class="text-center text-danger mt-4">
      <p>{{ summaryStore.error }}</p>
    </div>
    <div v-else>
        <div style="display: flex; gap: 20rem; justify-content: center; flex-wrap: wrap;">
            <div v-if="summaryStore.durationchartData && summaryStore.durationchartData.datasets?.length" style="flex: 1 1 600px; min-width: 200px; max-width: 400px;">
                <h4 class="text-center mb-2">Parking Lots Duration Summary</h4>
                <Bar :data="summaryStore.durationchartData" :options="summaryStore.durationchartOptions" />
            </div>
            <div v-if="summaryStore.revenuechartData && summaryStore.revenuechartData.datasets?.length" style="flex: 1 1 600px; min-width: 200px; max-width: 400px;">
                <h4 class="text-center mb-2">Parking Lots Revenue Summary</h4>
                <Bar :data="summaryStore.revenuechartData" :options="summaryStore.revenuechartOptions" />
            </div>
        </div>
        <p style="margin: 5px 0;"></p>
        <div v-if="summaryStore.bookingchartData && summaryStore.bookingchartData.datasets?.length" style="max-width: 400px; margin: 2rem auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 class="mb-0">Booking Overview</h4>
                <button  v-if="auth_store.isAuthenticated  && auth_store.getUserRole() == 'admin'" class="btn btn-success" @click="exportdatatocsv">Export CSV Report</button>
            </div>
            <p style="font-size: 0.95rem; margin-bottom: 1rem; color: #555;">
                <strong>Total Bookings:</strong> {{ summaryStore.bookingchartData.datasets[0].data[0] + summaryStore.bookingchartData.datasets[0].data[1] }}
                &nbsp;=&nbsp;
                <span style="color: #2ecc71;"><strong>Completed:</strong> {{ summaryStore.bookingchartData.datasets[0].data[0] }}</span>
                &nbsp;+&nbsp;
                <span style="color: #e74c3c;"><strong>Ongoing:</strong> {{ summaryStore.bookingchartData.datasets[0].data[1] }}</span>
            </p>
            <div style="width: 300px; height: 300px; margin: 0 auto;">
                <Pie :data="summaryStore.bookingchartData" :options="summaryStore.bookingchartOptions"/>
            </div>
        </div>
    </div>         
  </div> 
</template>