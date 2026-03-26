import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authstore.js'

export const useSummaryStore = defineStore('summary', () => {
  const auth_store = useAuthStore()
  const summarisedLots = ref([])
  const summarisedSpots = ref([])
  const revenuechartData = ref(null)
  const durationchartData = ref(null)
  const bookingchartData = ref(null)
  const revenuechartOptions = ref(null)
  const durationchartOptions = ref(null)
  const bookingchartOptions = ref(null)
  const bookingcount = ref(0)
  const completedbookings = ref(0)
  const ongoingbookings = ref(0)
  const totalduration = ref(0)
  const totalrevenue = ref(0)
  const loading = ref(false)
  const error = ref(null)

  async function fetchSummary() {
    try {
      loading.value = true
      error.value = null

      bookingcount.value = 0
      completedbookings.value = 0
      ongoingbookings.value = 0
      totalrevenue.value = 0
      totalduration.value = 0
      summarisedLots.value = []
      summarisedSpots.value = []
      revenuechartData.value = null
      durationchartData.value = null
      bookingchartData.value = null

      const token = auth_store.getAuthToken()
      const userid = auth_store.getUserid()
      const userrole = auth_store.getUserRole()
      let fetchurl = ''
      if (!token) throw new Error('User not authenticated')

      if (userrole == 'admin'){
        fetchurl = 'http://127.0.0.1:5000/api/bookingspot'
      } else {
        fetchurl = "http://127.0.0.1:5000/api/bookingspot/user/"+ userid
      } 
      //Fetch reservation (booking) data
      const reserverRes = await fetch(fetchurl, {
        headers: { 'authentication-token': token },
      })

      if (!reserverRes.ok) throw new Error('Failed to fetch booking data')
      const data = await reserverRes.json()

      //Process data for lot and spot summaries
      const summarisedSpotsMap = new Map()
      const summarisedLotsMap = new Map()
      for (const reservation of data) {
        bookingcount.value += 1
        if (reservation.leavingtime != null){
            completedbookings.value += 1
        }
        const start = new Date(reservation.parkingtime)
        const end = new Date(reservation.leavingtime)
        const duration = reservation.leavingtime
          ? Math.ceil((end - start) / (1000 * 60 * 60))
          : 0

        // --- Spots summary ---
        if (!summarisedSpotsMap.has(reservation.spotid)) {
          summarisedSpotsMap.set(reservation.spotid, {
            spotid: reservation.spotid,
            lotid: reservation.lotid,
            location: reservation.location,
            duration,
            parkingcost: reservation.leavingtime != null ? reservation.parkingcost : 0 //|| 0,
          })
        } else {
          const existing = summarisedSpotsMap.get(reservation.spotid)
          existing.duration += duration
          existing.parkingcost += reservation.leavingtime != null ? reservation.parkingcost: 0// || 0
        }

        // --- Lots summary ---
        if (!summarisedLotsMap.has(reservation.lotid)) {
          summarisedLotsMap.set(reservation.lotid, {
            lotid: reservation.lotid,
            location: reservation.location,
            duration,
            parkingcost: reservation.leavingtime != null ? reservation.parkingcost : 0 //|| 0
          })
        } else {
          const existing = summarisedLotsMap.get(reservation.lotid)
          existing.duration += duration
          existing.parkingcost += reservation.leavingtime != null ? reservation.parkingcost: 0// || 0
        }
      }
      ongoingbookings.value = bookingcount.value - completedbookings.value
      summarisedLots.value = Array.from(summarisedLotsMap.values())
      totalduration.value = summarisedLots.value.reduce((sum, lot) => sum + (lot.duration || 0), 0)
      totalrevenue.value = summarisedLots.value.reduce((sum, lot) => sum + (lot.parkingcost || 0), 0)
      summarisedLots.value.sort((a,b) => b.parkingcost - a.parkingcost)
      summarisedSpots.value = Array.from(summarisedSpotsMap.values())

      //Bar chart for duration 
      durationchartData.value = {
        labels: summarisedLots.value.map(item => `${item.location} (Lot ${item.lotid})`),
        datasets: [
          {
            label: 'Duration      [Total Duration:' + totalduration.value +' (hrs) ]',
            data: summarisedLots.value.map(item => item.duration),
            backgroundColor: '#2ecc71',
          },
        ],
      }
      //Bar cahrt for revenue
      revenuechartData.value = {
        labels: summarisedLots.value.map(item => `${item.location} (Lot ${item.lotid})`),
        datasets: [
          {
            label: 'Revenue       [Total Revenue: (Rs)' + totalrevenue.value + ' ]',
            data: summarisedLots.value.map(item => item.parkingcost),
            backgroundColor: '#3498db',
          },          
        ],
      }
      //Pie chart for bookings
      bookingchartData.value = {
        labels: ['Completed Bookings', 'Ongoing Bookings'],
        datasets :[
            {
                data:[
                    completedbookings.value,
                    ongoingbookings.value,
                ],
                backgroundColor: ['#2ecc71', '#e74c3c'],
                hoverOffset: 10, 
            },
        ],               
      }

      durationchartOptions.value = {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
        },
      }
      revenuechartOptions.value = {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
        },
      }
      bookingchartOptions.value = {
        responsive: true,
        plugins: {
            legend: { position: 'top', labels: {boxWidth: 20, padding: 15,} },
            tooltip: {
                callbacks: {
                    label(context) {
                        const label = context.label || ''
                        const value = context.parsed || 0
                        const data = context.dataset.data
                        const total = data.reduce((a, b) => a + b, 0)
                        const percent = ((value / total) * 100).toFixed(1)
                        return `${label}: ${value} (${percent}%)`
                    }
                }
            }
        }
      }
    } catch (err) {
      console.error('Error fetching summary:', err)
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return {
    summarisedLots,
    summarisedSpots,
    durationchartData,
    revenuechartData,
    bookingchartData,
    durationchartOptions,
    revenuechartOptions,
    bookingchartOptions,
    loading,
    error,
    fetchSummary,
  }
})
