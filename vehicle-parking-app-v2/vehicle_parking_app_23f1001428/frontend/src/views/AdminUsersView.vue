<script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useAuthStore } from '@/stores/authstore.js';
  import { nextTick } from 'vue'

  const auth_store = useAuthStore();

  const users = ref([])
  const rspots = ref([]) 
  const selectedusername = ref('')

  
  // Fetch all users once
  onMounted(async () => {
    await nextTick()  // Wait for DOM to render

    //Registered Users
    try {      
      const token = auth_store.getAuthToken()

      const response = await fetch("http://127.0.0.1:5000/api/users", {
        headers: {
          "authentication-token": token
        }
      })
      if (!response.ok) {
        const error = await response.json()
        console.error('Error fetching users:', error.message)
        return
      }
      const data = await response.json()
      users.value = data
    } catch (error) {
        console.error('Failed to fetch users:', error)
    }
    //Get all reservation details
  try {         
      const token = auth_store.getAuthToken()
      
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

  const filteredrspots = computed(() => {
    if (!selectedusername.value) {
      return rspots.value
    }
    return rspots.value.filter(rspot => rspot.username== selectedusername.value)
  })

  function onUserChange() {
    //selectedresdetails.value = rspots.value.find(rspot => rspot.username === selectedusername.value)
    filteredrspots.value=rspots.value.find(rspot => rspot.username === selectedusername.value)
  }

  function clearUser() {
    selectedusername.value = '';
  }
  
</script>

<template>
  <div class="container py-4">
    <nav class="navbar navbar-expand-lg bg-dark py-1" data-bs-theme="dark"> 
      <div class="container-fluid">
        <ul class="navbar-nav me-auto"> 
          <li class="nav-item">
              <h5 class="nav-link active mb-0" aria-current="page"><b>Registered Users Detail</b></h5>
          </li>
        </ul>
      </div>
    </nav>
    <!-- Display reservation Details -->
    <div style="max-height:200px; overflow-y:auto;">  
      <table class="table table-bordered table-hover align-middle text-center">    
        <thead class="table-secondary">
              <tr>
                <th>ID</th>
                <th>User/Email</th>
                <th>Full Name</th>
                <th>Address</th>
                <th>PinCode</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.fullname }}</td>
                <td>{{ user.address }}</td>
                <td>{{ user.pincode }}</td>
              </tr>
            </tbody>
      </table>
    </div>
  </div>
  <div class="container py-4">
    <nav class="navbar navbar-expand-lg bg-dark py-1" data-bs-theme="dark"> 
      <div class="container-fluid">
        <ul class="navbar-nav me-auto"> 
          <li class="nav-item">
              <h5 class="nav-link active" aria-current="page"><b>Reservations History @ All Users</b></h5>
          </li>
        </ul>
      </div>
      <!--<form class="d-flex align-items-center">-->
      <form class="d-flex flex-nowrap align-items-center gap-1">
          <label class="me-2 mb-0">Select User:</label>
          <select class="form-select form-select-sm me-2 w-auto" v-model="selectedusername" @change="onUserChange">
            <option disabled value="">-- Choose User--</option>
              <option v-for="user in users" :key="user.id" :value="user.fullname"> {{ user.fullname }} </option>
          </select>
          <button type="button" class="btn btn-outline-secondary" @click="clearUser">Clear</button>    
      </form>
    </nav>
    <!-- Display reservation Details -->
    <div style="max-height:200px; overflow-y:auto;">  
      <table class="table table-bordered table-hover align-middle text-center">    
        <thead class="table-secondary">
          <tr>
            <th>User</th>
            <th>Location</th>
            <th>Spot</th>
            <th>Vehicle</th>
            <th>Time of booking</th>
            <th>Time of Leaving</th>
            <th>Parking Cost (Rs/hr)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rspot in filteredrspots" :key="rspot.id">
            <td>{{ rspot.username }}</td>
            <td>{{ rspot.location }}</td>
            <td>{{ rspot.spotid }}</td>
            <td>{{ rspot.vehicleno }}</td>
            <td>{{ rspot.parkingtime }}</td>
            <td>{{ rspot.leavingtime }}</td>
            <td>{{ rspot.leavingtime ? rspot.parkingcost : null }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>  
