<script setup>
import { useAuthStore } from '@/stores/authstore.js';
import { ref, onMounted, watch, computed } from 'vue'

import ParkingLot from '@/components/ParkingLot.vue';
import AddLotModal from './AddLotModal.vue'
import EditLotModal from './EditLotModal.vue'

const plots = ref([])
const rspots = ref([]) 
const currentLot = ref(null)
const addModalRef = ref(null)
const editModalRef = ref(null)

let summarisedArray = ref([])
let summarisedLotArray = ref([])
const selectedLotId = ref(null)

// when admin component is loaded, lot and spot data needs to be fetched and shown 
onMounted(async () => {
  try {
    const token = auth_store.getAuthToken()

    const response = await fetch("http://127.0.0.1:5000/api/parkinglot", {
      headers: {
        "authentication-token": token
      }
    })
    if (!response.ok) {
      throw new Error('failed while fetching parking lots')
    }
    const data = await response.json()
    // Normalize the backend data to match your card layout
    plots.value = data.map(lot => ({
      id: lot.id,
      status: lot.status,
      location: lot.location,                 // UI expects 'location'
      address: lot.address,
      price: lot.price.toString(),
      pincode: lot.pincode.toString(),
      noofspots: (lot.noofspots ?? 0).toString(),
      spots: lot.spots || []             // Ensure it's an array
    })) 
    for (const plot of plots.value){
      plot.spots = plot.spots.filter(spot => spot.status !== 'D');       
    }
  } catch (err) {
    console.error('Error loading plots:', err)
  }
  //Get all reservation details
  try {         
      const token = auth_store.getAuthToken()
      const userid = auth_store.getUserid()

      const reserverres = await fetch("http://127.0.0.1:5000/api/bookingspot", {
        headers: {
          "authentication-token": token
        }
      })
      if (!reserverres.ok) {
        throw new Error('failed while fetching reservation details')
      }
      
      const data = await reserverres.json()
      rspots.value = data.map(reservation => {
        return {
          id: reservation.id,
          username: reservation.username,
          lotid: reservation.lotid,
          location: reservation.location,
          spotid: reservation.spotid,
          vehicleno: reservation.vehicleno,
          parkingtime: reservation.parkingtime,
          leavingtime: reservation.leavingtime,
          parkingcost: reservation.parkingcost,
          duration: reservation.leavingtime ? getParkDurationInHours(getformattedDateTime(reservation.parkingtime), 
                                  getformattedDateTime(reservation.leavingtime)) : null                   
        }        
      })
      //summarise the spot parking revenu and parking duration
      const summarisedSpots = new Map();
      for (const rspot of rspots.value) {
        const key = rspot.spotid;
        if (!summarisedSpots.has(key)) {
          summarisedSpots.set(key, {
            spotid: key,
            duration: rspot.duration,
            parkingcost: rspot.parkingcost,
            location: rspot.location,
            parkingtime: rspot.parkingtime,
            leavingtime: rspot.leavingtime,
            lotid: rspot.lotid
          });
        } else {  
          const existing = summarisedSpots.get(key);
          existing.duration += rspot.duration;
          existing.parkingcost += rspot.leavingtime ? rspot.parkingcost : 0;
        }
      }
      summarisedArray.value = Array.from(summarisedSpots.values());

      //summarise the lot parking revenu and parking duration
      const summarisedLots = new Map();
      for (const rspot of rspots.value) {
        const key = rspot.lotid;
        if (!summarisedLots.has(key)) {
          summarisedLots.set(key, {
            lotid: key,
            duration: rspot.duration,
            parkingcost: rspot.parkingcost,
            location: rspot.location,
          });
        } else {  
          const existing = summarisedLots.get(key);
          existing.duration += rspot.duration;
          existing.parkingcost += rspot.leavingtime ? rspot.parkingcost : 0;
        }
      }
      summarisedLotArray.value = Array.from(summarisedLots.values());      
    } catch (error) {
      console.error('Failed to fetch lots:', error)
    }
})

function getformattedDateTime(datetimeString){
    const date = new Date(datetimeString)

    const year = date.getUTCFullYear()
    const month = String(date.getUTCMonth() + 1).padStart(2, '0')
    const day = String(date.getUTCDate()).padStart(2, '0')
    const hours = String(date.getUTCHours()).padStart(2, '0')
    const minutes = String(date.getUTCMinutes()).padStart(2, '0')
    const seconds = String(date.getUTCSeconds()).padStart(2, '0')
     return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  function getParkDurationInHours(startDateStr, endDateStr){
    const startDt = new Date(startDateStr)
    const endDt = new Date(endDateStr)

    const start = Date.UTC(startDt.getUTCFullYear(), startDt.getUTCMonth(), startDt.getUTCDate(),startDt.getUTCHours(), startDt.getUTCMinutes(), startDt.getUTCSeconds())
    const end = Date.UTC(endDt.getUTCFullYear(), endDt.getUTCMonth(), endDt.getUTCDate(),endDt.getUTCHours(), endDt.getUTCMinutes(), endDt.getUTCSeconds())
    const durationMs = end - start
    const durationHours = Math.ceil(durationMs / (1000 * 60 * 60))

    return durationHours
  }

const getBlankModal = () => {
  addModalRef.value?.showModal()
}

//Code for adding a lot
const addLot = (data) => {
  const token = auth_store.getAuthToken()
  const lotdetails = {
    location_name: data.location_name,
    address: data.address,
    price: data.price,
    pincode: data.pincode,
    noofspots: data.spots    
  }
  const response = fetch("http://127.0.0.1:5000/api/parkinglot", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "authentication-token": token
            },
            body: JSON.stringify(lotdetails)            
  }).then(response => {
    if (!response.ok) {
      alert("Failed to add parking lot")
    }
    return response.json();
  }).then(data => {
    const lot = data.data;
    const normalizedLot = {
      id: lot.id,
      status: lot.status,
      location: lot.name,                 
      address: lot.address,
      price: lot.price.toString(),        
      pincode: lot.pincode.toString(),
      noofspots: lot.noofspots.toString(),
      spots: lot.spots || []                           
    };
    plots.value.push(normalizedLot);
  }).catch(error => {
    console.error("Error:", error);
  });  
} 

const handleEdit = (lot) => {
  currentLot.value = lot
  editModalRef.value?.showModal() 
}

//code for editing a lot
const updateLot = async (updatedLot) => {
  const lotid = updatedLot.id;
  const token = auth_store.getAuthToken();

  const updatedlotdetails = {
    location: updatedLot.location,
    address: updatedLot.address,
    price: updatedLot.price,
    pincode: updatedLot.pincode,
    noofspots: updatedLot.noofspots    
  };

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/parkinglot/${lotid}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "authentication-token": token
      },
      body: JSON.stringify(updatedlotdetails)
    });

    const data = await response.json();

    if (!response.ok) {
      alert(data.message || "Failed to update parking lot");
      return;
    }

    const lot = data.data;
    const normalizedLot = {
      id: lot.id,
      status: lot.status,
      location: lot.location,                  
      address: lot.address,
      price: lot.price.toString(),        
      pincode: lot.pincode.toString(),
      noofspots: lot.noofspots.toString(),
      spots: lot.spots || []                           
    };
    
    const index = plots.value.findIndex(l => l.id === lotid);
    if (index !== -1) {
      plots.value[index] = normalizedLot;
      plots.value = [...plots.value]; 
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Something went wrong while updating the parking lot");
  }
};

const handleLotDelete = async (lot) => {
  // confirm and delete....call API
  const token = auth_store.getAuthToken()
  const lotid=lot.id
  try {
    const response = await fetch("http://127.0.0.1:5000/api/parkinglot/" + lotid, {
              method: "DELETE",
              headers: {
                  "Content-Type": "application/json",
                  "authentication-token": token
              },
          })
          const res = await response.json()
          const resmsg = res.message
          if (!response.ok) {
            alert(resmsg)
          } else {
            alert("Successfully deleted the lot/location: " + lot.location)
            // Remove the deleted lot from `plots`
            plots.value = plots.value.filter(p => p.id !== lot.id);
          }          
         } catch (error) {
            console.error("Error:", error)
        }
}

const handleDeletedSpot = ({ lotId, spotId }) => {
  const lot = plots.value.find(p => p.id === lotId);
  if (lot) {
    lot.spots = lot.spots.filter(s => s.spotid !== spotId);
  }
}

const filteredSpotSummary = computed(() => {
  if (!selectedLotId.value) {
    return []
  }
  // filter spots by lotid matching selectedLotId
  return summarisedArray.value.filter(item => item.lotid === selectedLotId.value);
})

const auth_store = useAuthStore();
</script>

<template>
  <div class="container py-1">
    <nav class="navbar navbar-expand-lg py-0" style="background-color: #2c3a50;" data-bs-theme="dark">  
      <div class="container-fluid">
        <ul class="navbar-nav me-auto"> 
          <li class="nav-item" v-if="auth_store.isAuthenticated">
              <p class="nav-link active" aria-current="page"><b>Parking Lots & Spots</b><i>(click on spots[red:Occupied;green:Available] to get details)</i></p>
          </li>
        </ul>
        <ul>  
          <li class="nav-item" v-if="auth_store.isAuthenticated">
              <button class="btn btn-sm btn-primary" @click="getBlankModal">+ Add New Lot</button>
              <AddLotModal ref="addModalRef" @add_lot="addLot" />
          </li> 
        </ul> 
      </div>
    </nav>
  </div>      
  <div class="container">
    <!-- Horizontally scrollable parent cards -->
    <EditLotModal ref="editModalRef" :lot="currentLot" @edit_lot="updateLot" />
    <div class="d-flex overflow-auto gap-3 pb-0" style="white-space: nowrap;">
        <ParkingLot v-for="plot in plots.filter(p => p.status !== 'D')" :key="plot.id" class="flex-shrink-0" style="width: 300px"  :parkinglot="plot" @edit_lot="handleEdit" @delete_lot="handleLotDelete" @spot_deleted="handleDeletedSpot"/>
    </div>  
  </div>
  <div class="container py-4">
    <nav class="navbar navbar-expand-lg bg-dark py-0" data-bs-theme="dark"> 
      <div class="container-fluid">
        <div class="d-flex align-items-center">
          <ul class="navbar-nav me-auto"> 
            <li class="nav-item">
                <h5 class="nav-link active mb-0" aria-current="page"><b>Parking History</b></h5>
            </li>
          </ul>
        </div>
        <div class="d-flex align-items-center mb-1">
          <label for="lotFilter" class="me-2 text-white">Breakdown by Lot ID:</label>
          <select id="lotFilter" v-model="selectedLotId" class="form-select w-auto">
            <option :value="null">All Lots</option>
            <option v-for="plot in plots" :key="plot.id" :value="plot.id">{{ plot.id }} - {{ plot.location }}</option>
          </select>
        </div>
      </div>  
    </nav>
    <!-- Display reservation Details- lot level -->
    <div style="max-height:200px; overflow-y:auto;">  
      <table class="table table-bordered table-hover align-middle text-center">    
        <thead class="table-secondary">
          <tr>
            <th>LotId</th>
            <th>Location</th>
            <th>Overall Parking Revenu (Rs)</th>
            <th>Overall Booking Duration (hrs)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rspot in summarisedLotArray" :key="rspot.id">  
            <td>{{ rspot.lotid }}</td>
            <td>{{ rspot.location }}</td>
            <td>{{ rspot.parkingcost }}</td>
            <td>{{ rspot.duration }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <!-- Display reservation Details- spot level -->
    <div v-if="selectedLotId && filteredSpotSummary.length > 0" style="max-height:200px; overflow-y:auto;"> 
      <nav class="navbar navbar-expand-lg bg-dark py-0" data-bs-theme="dark">
        <ul class="navbar-nav me-auto"> 
          <li class="nav-item">
            <!--<p class="nav-link active" aria-current="page"><b>Reservations History</b></p>-->
            <h5 class="nav-link active mb-0" aria-current="page"><b>Parking Details Breakdown@ LotID :- {{ selectedLotId }}</b></h5>
          </li>
        </ul> 
      </nav> 
      <table class="table table-bordered table-hover align-middle text-center">    
        <thead class="table-secondary">
          <tr>
            <th>LotId</th>
            <th>Location</th>
            <th>Spot</th>
            <th>Overall Revenu for Spot@location (Rs)</th>
            <th>Overall Booked Duration for Spot@location (hrs)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rspot in filteredSpotSummary" :key="rspot.id">  
            <td>{{ rspot.lotid }}</td>
            <td>{{ rspot.location }}</td>
            <td>{{ rspot.spotid }}</td>
            <td>{{ rspot.leavingtime ? rspot.parkingcost : null }}</td>
            <td>{{ rspot.leavingtime ? rspot.duration : null }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>    
