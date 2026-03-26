<script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useAuthStore } from '@/stores/authstore.js';
  import { nextTick } from 'vue'

  const auth_store = useAuthStore();

  const plots = ref([]) 
  const rspots = ref([])                 
  const selectedLotId = ref('')
  const selectedLotDetails = ref(null) 
  
  const bookingModalRef = ref(null)
  let bookingModalInstance = null 
  const releaseModalRef = ref(null)
  let releaseModalInstance = null 

  // Fetch all lots and users reservations once
  onMounted(async () => {
    await nextTick()  // Wait for DOM to render

    if (bookingModalRef.value) {
      bookingModalInstance = new bootstrap.Modal(bookingModalRef.value)
      //bookingModalInstance.show()
    }
    if (releaseModalRef.value) {
      releaseModalInstance = new bootstrap.Modal(releaseModalRef.value)
    }
    //get all available lots
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
      plots.value = data.map(lot => {
        const spots = lot.spots || []
        const available_spots = spots.filter(spot => spot.status === 'A');
        return {
          id: lot.id,
          status: lot.status,
          location: lot.location,                 
          address: lot.address,
          price: lot.price.toString(),
          pincode: lot.pincode.toString(),
          noofspots: lot.noofspots.toString(),
          noofavailablespots: available_spots.length,
          spots: spots                      
        }        
      })
    } catch (error) {
      console.error('Failed to fetch lots:', error)
    }
    // Get all users reservations
    try {     
      
      const token = auth_store.getAuthToken()
      const userid = auth_store.getUserid()

      const reserverres = await fetch("http://127.0.0.1:5000/api/bookingspot/user/"+ userid, {
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
          lotid: reservation.lotid,
          location: reservation.location,
          spotid: reservation.spotid,
          vehicleno: reservation.vehicleno,
          parkingtime: reservation.parkingtime,
          leavingtime: reservation.leavingtime,
          parkingcost: reservation.parkingcost                   
        }        
      })
    } catch (error) {
      console.error('Failed to fetch lots:', error)
    }
  })

  const locations = computed(() => {
    return plots.value.map(plot => ({
      id: plot.id,
      name: plot.location
    }))
  })
  
  // Filtered lots based on dropdown selection
  const filteredLots = computed(() => {
    if (!selectedLotId.value) {
      return plots.value
    }
    return plots.value.filter(lot => lot.id === Number(selectedLotId.value))
  })

  // When dropdown changes, find the lot in `plots`
  function onLocationChange() {
    selectedLotDetails.value = plots.value.find(lot => lot.id === Number(selectedLotId.value))
    if (selectedLotDetails.value && selectedLotDetails.value.spots) {
      const availableSpots = selectedLotDetails.value.spots.filter(spot => spot.status === 'A');
    }
  }

  function clearLocation() {
    selectedLotId.value = ''
    selectedLotDetails.value = null
  }

  const bookingDetails = ref({
    spotid: '',
    lotid: '',
    userid: '',
    vehicleno: ''
  })

  // Booking Modal
  function getBookingModal(lot) {
    if (!lot || !Array.isArray(lot.spots)) 
      return
    const availableSpot = lot.spots.find(s => s.status === 'A')
    if (!availableSpot) return

    bookingDetails.value = {
      spotid: availableSpot.spotid,
      lotid: lot.id,
      userid: auth_store.getUserid(),  
      vehicleno: ''
    }
    if (bookingModalInstance) {
      bookingModalInstance.show()
    }
  }

  async function bookSpot(lot_id) {
    if (bookingDetails.value.vehicleno == ''){
      alert('Please enter vehicle details')
    }
    try {
      const token = auth_store.getAuthToken();

      const response = await fetch('http://127.0.0.1:5000/api/bookingspot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'authentication-token': token
        },
        body: JSON.stringify(bookingDetails.value)  
      })
      if (!response.ok) {
        throw new Error('Failed to book spot');
      }

      alert('Spot reserved successfully!')
      closeBookingModal()
      await refreshLots()
      await refreshUserReservations()
    } catch (err) {
      alert(err.message);
    }
  }

  function closeBookingModal() {
    if (bookingModalInstance) {
      bookingModalInstance.hide()
    } else {
      console.warn("modal instance is not yet defined")
    }
  }

  //For refreshing lot
  async function refreshLots() {
  try {
    const token = auth_store.getAuthToken();

    const response = await fetch("http://127.0.0.1:5000/api/parkinglot", {
      headers: {
        "authentication-token": token
      }
    });
    if (!response.ok) {
      throw new Error('Failed to refresh lots');
    }

    const data = await response.json();
    plots.value = data.map(lot => {
      const spots = lot.spots || []
      const available_spots = spots.filter(spot => spot.status === 'A');
      return {
        id: lot.id,
        status: lot.status,
        location: lot.location,
        address: lot.address,
        price: lot.price.toString(),
        pincode: lot.pincode.toString(),
        noofspots: lot.noofspots.toString(),
        noofavailablespots: available_spots.length,
        spots: spots
      };
    });
  } catch (error) {
    console.error('Failed to refresh lots:', error);
  }
}

//For refreshing user's reservation history
async function refreshUserReservations() {
  try {
    const token = auth_store.getAuthToken();
    const userid = auth_store.getUserid();

    const response = await fetch(`http://127.0.0.1:5000/api/bookingspot/user/${userid}`, {
      headers: {
        "authentication-token": token
      }
    });

    if (!response.ok) {
      throw new Error('Failed to refresh reservations');
    }

    const data = await response.json();
    rspots.value = data.map(reservation => ({
      id: reservation.id,
      lotid: reservation.lotid,
      location: reservation.location,
      spotid: reservation.spotid,
      vehicleno: reservation.vehicleno,
      parkingtime: reservation.parkingtime,
      leavingtime: reservation.leavingtime,
      parkingcost: reservation.parkingcost
    }));
  } catch (error) {
    console.error('Failed to refresh reservations:', error);
  }
}

const releaseDetails = ref({
    reserveid : '',
    spotid: '',
    vehicle: '',
    parkingtime: '',
    releasingtime: '',
    totalcost: ''
})

//Release Modal
function getReleaseModal(reservespot) {
    if (!reservespot) 
      return
            
    const startTimeFormatted = getformattedDateTime(reservespot.parkingtime)
    const endTimeFormatted = getCurrentDateTimeString()
   
    const durationHours = getParkDurationInHours(startTimeFormatted, getCurrentDateTimeString())
    const totalcost = durationHours * reservespot.parkingcost;
    
    releaseDetails.value = {
      reserveid: reservespot.id,
      spotid: reservespot.spotid,
      vehicle: reservespot.vehicleno,
      parkingtime: startTimeFormatted,
      releasingtime: endTimeFormatted,
      totalcost: totalcost
    }
    if (releaseModalInstance) {
      releaseModalInstance.show()
    }
  }

  function getCurrentDateTimeString() {
    const now = new Date();

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');

    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }


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

  //Release the spot
  async function releaseSpot(reserveid) {
    try {
      const token = auth_store.getAuthToken();

      const response = await fetch("http://127.0.0.1:5000/api/bookingspot/reservation/" + reserveid, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'authentication-token': token
        },
       })

      if (!response.ok) {
        throw new Error('Failed to release spot');
      }
      const resp = await response.json()
      
      alert('Spot released successfully!');
      const releasedSpot = rspots.value.find(rspot => rspot.id === reserveid)
      releasedSpot.leavingtime = resp.data.leavingtime
      releasedSpot.parkingcost = resp.data.parkingcost
      
      closeReleaseModal()
      await refreshLots()
      await refreshUserReservations()
    } catch (err) {
      alert(err.message);
    }
  }

  function closeReleaseModal() {
    if (releaseModalInstance) {
      releaseModalInstance.hide()
    } else {
      console.warn("release modal instance is not yet defined")
    }
  }

</script>

<template>
  <!--Lot and spot availability detail -->
  <div class="container py-2">
    <nav class="navbar navbar-expand-lg bg-dark" data-bs-theme="dark"> 
      <div class="container-fluid">
        <ul class="navbar-nav me-auto"> 
          <li class="nav-item">
              <p class="nav-link active" aria-current="page"><h5>Parking Lot Details</h5></p>
          </li>
        </ul>
        <form class="d-flex align-items-center">
          <label class="me-2 mb-0">Select Location:</label>
          <select class="form-select me-2" v-model="selectedLotId" @change="onLocationChange">
            <option disabled value="">-- Choose Location --</option>
              <option v-for="loc in locations" :key="loc.id" :value="loc.id"> {{ loc.name }} </option>
          </select>
          <button type="button" class="btn btn-outline-secondary" @click="clearLocation">Clear</button>    
      </form>
      </div>
    </nav>    
    <div style="max-height:200px; overflow-y:auto;">
      <table class="table table-bordered table-hover align-middle text-center">  
        <thead class="table-secondary">
          <tr>
            <th>ID</th>
            <th>Location</th>
            <th>Address</th>
            <th>Available Spots</th>
            <th>Price/hr</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in filteredLots.filter(p => p.status !== 'D')" :key="lot.id">
            <td>{{ lot.id }}</td>
            <td>{{ lot.location }}</td>
            <td>{{ lot.address }}</td>
            <td>{{ lot.noofavailablespots }}</td>
            <td>{{ lot.price }}</td>
            <td><button class="btn btn-primary" :disabled="lot.noofavailablespots === 0" @click="getBookingModal(lot)"> Book </button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <!-- User booking history-->
  <div class="container py-4">
    <nav class="navbar navbar-expand-lg bg-dark py-1" data-bs-theme="dark"> 
      <div class="container-fluid">
        <ul class="navbar-nav me-auto"> 
          <li class="nav-item">
              <h5 class="nav-link active" aria-current="page"><b>Reservations History</b></h5>
          </li>
        </ul>
      </div>
    </nav>
    <!-- Display Lot Details After Selection -->
    <div style="max-height:200px; overflow-y:auto;">
      <table class="table table-bordered table-hover align-middle text-center">    
        <thead class="table-secondary">
          <tr>
            <th>ID</th>
            <th>Location</th>
            <th>Spot</th>
            <th>Vehicle</th>
            <th>Time of booking</th>
            <th>Time of Leaving</th>
            <th>Parking Cost</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rspot in rspots" :key="rspot.id">
            <td>{{ rspot.id }}</td>
            <td>{{ rspot.location }}</td>
            <td>{{ rspot.spotid }}</td>
            <td>{{ rspot.vehicleno }}</td>
            <td>{{ rspot.parkingtime }}</td>
            <td>{{ rspot.leavingtime }}</td>
            <td>{{ rspot.leavingtime ? rspot.parkingcost : null }}</td>
            <td><button class="btn btn-primary" @click="getReleaseModal(rspot)" :disabled="rspot.leavingtime != null"> Release </button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <!-- Booking Modal using Bootstrap -->
  <div class="modal fade" id="bookingModal" tabindex="-1" ref="bookingModalRef" aria-labelledby="bookingModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="bookingModalLabel">Reserve Parking Spot</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-2">
            <label>Spot ID</label>
            <input type="text" class="form-control" v-model="bookingDetails.spotid" readonly />
          </div>
          <div class="mb-2">
            <label>Lot ID</label>
            <input type="text" class="form-control" v-model="bookingDetails.lotid" readonly />
          </div>
          <div class="mb-2">
            <label>User ID</label>
            <input type="text" class="form-control" v-model="bookingDetails.userid" readonly />
          </div>
          <div class="mb-2">
            <label>Vehicle Number</label>
            <input type="text" class="form-control" v-model="bookingDetails.vehicleno"  required/>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-success" @click="bookSpot">Reserve</button>
          <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        </div>
      </div>
    </div>
  </div>
  <!-- Release Modal using Bootstrap -->
  <div class="modal fade" id="releaseModal" tabindex="-1" ref="releaseModalRef" aria-labelledby="releaseModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="releaseModalLabel">Release Parking Spot</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="mb-2">
            <label>Spot ID</label>
            <input type="text" class="form-control" v-model="releaseDetails.spotid" readonly />
          </div>
          <div class="mb-2">
            <label>vehicle</label>
            <input type="text" class="form-control" v-model="releaseDetails.vehicle" readonly />
          </div>
          <div class="mb-2">
            <label>Parking Time</label>
            <input type="text" class="form-control" v-model="releaseDetails.parkingtime" readonly />
          </div>
          <div class="mb-2">
            <label>Releasing Time</label>
            <input type="text" class="form-control" v-model="releaseDetails.releasingtime" />
          </div>
          <div class="mb-2">
            <label>Total Cost</label>
            <input type="text" class="form-control" v-model="releaseDetails.totalcost" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-success" @click="releaseSpot(releaseDetails.reserveid)">Release</button>
          <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>    
