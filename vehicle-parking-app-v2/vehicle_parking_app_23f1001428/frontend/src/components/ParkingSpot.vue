<script setup>
    import {ref} from 'vue';
    import { useAuthStore } from '@/stores/authstore.js';
        
    const props = defineProps(['parkingSpot'])
    const auth_store = useAuthStore();
    const emit = defineEmits(['spot_deleted'])

    // Modal state
    const deleteModal = ref(false)
    const reservemodal = ref(false)
    const spotId = ref('')
    const spotStatus = ref('')
    const token = auth_store.getAuthToken()

    // Open modal and populate fields
    function openDeleteModal() {
        spotId.value = props.parkingSpot.spotid
        spotStatus.value = props.parkingSpot.status
        deleteModal.value = true
    }

    // Close modal
    function closeDeleteModal() {
        deleteModal.value = false
    }

    // DELETE API call
    async function deleteSpot() {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/parkingspot/spot/${spotId.value}`, {
        headers: {
          "Content-Type": "application/json",
          "authentication-token": token
        },  
        method: 'DELETE'
        })

        if (response.ok) {
          alert(`Spot ${spotId.value} deleted successfully`)
          emit('spot_deleted', { spotid: spotId.value })
        } else {
          const res = await response.json();
          alert(res.message)
        }
    } catch (error) {
        console.error('Error deleting spot:', error)
    }
    closeDeleteModal()
  }

  // Reservation Data
  const reservationDetails = ref({
    spotid: '',
    user_id: '',
    vehicle_no: '',
    parking_time: '',
    estimated_cost: ''
  })

  // Open Reservation Modal from inside Delete Modal
  async function openReservationModal() {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/bookingspot/spot/${spotId.value}`)
      const data = await response.json()
      reservationDetails.value = {
        spotid: data.spotid,
        user_id: data.userid,
        vehicle_no: data.vehicleno,
        parking_time: data.parkingtime,
        estimated_cost: data.parkingcost
      }
      reservemodal.value = true
    } catch (error) {
        console.error('Error fetching reservation:', error)
    }
  }

    function closeReservationModal() {
        reservemodal.value = false
    }

</script>

<template>   
    <div class="card parking-spot border-secondary me-1" :class="props.parkingSpot.status === 'O' ? 'bg-danger' : 'bg-success'" @click="openDeleteModal" :title="`Click to view or delete this spot`">  
      <div class="card-body text-center d-flex align-items-center justify-content-center p-0" style="height: 40px;">
        <h6 class="m-0">{{ props.parkingSpot.spotid }}</h6>
      </div>
    </div>
    <!-- Delete Modal -->
    <div v-if="deleteModal" class="modal-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1050;">
        <div class="modal-box bg-white p-4 rounded" style="width: 250px;">
        <div class="modal-header d-flex justify-content-between align-items-center">
            <h5 class="modal-title">View/Delete Spot</h5>
            <button class="btn-close" @click="closeDeleteModal" style="border: none; background: none;">✕</button>
        </div>

        <div class="modal-body mt-3">
            <div class="mb-3">
            <label for="spotid" class="form-label">Spot ID</label>
            <input type="text" class="form-control" id="spotid" v-model="spotId" readonly />
            </div>
            <div class="mb-3">
              <label for="status" class="form-label">Status</label>
               <input class="form-control text-primary" type="text" v-model="spotStatus" readonlystyle="cursor: pointer;" @click= "spotStatus === 'O' && openReservationModal()"/>
              <small class="text-muted" v-if="spotStatus === 'O'">Click status to view details</small>
            </div>
        </div>
        <div class="modal-footer d-flex justify-content-end">
            <button class="btn btn-danger me-2" @click="deleteSpot" :disabled="spotStatus === 'O'">Delete</button>
            <button class="btn btn-secondary" @click="closeDeleteModal">Cancel</button>
        </div>
        </div>
    </div>
    <!-- RESERVATION DETAILS MODAL -->
  <div v-if="reservemodal" class="modal-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1050;">
    <div class="modal-box bg-white p-4 rounded" style="width: 400px;">
      <div class="modal-header">
        <h5 class="modal-title">Reservation Info</h5>
        <button class="btn-close" @click="closeReservationModal">✕</button>
      </div>
      <div class="modal-body">
        <div class="mb-2">
          <label>Spot ID</label>
          <input class="form-control" v-model="reservationDetails.spotid" readonly />
        </div>
        <div class="mb-2">
          <label>User ID</label>
          <input class="form-control" v-model="reservationDetails.user_id" readonly />
        </div>
        <div class="mb-2">
          <label>Vehicle No</label>
          <input class="form-control" v-model="reservationDetails.vehicle_no" readonly />
        </div>
        <div class="mb-2">
          <label>Parking Time</label>
          <input class="form-control" v-model="reservationDetails.parking_time" readonly />
        </div>
        <div class="mb-2">
          <label>Estimated Cost</label>
          <input class="form-control" v-model="reservationDetails.estimated_cost" readonly />
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeReservationModal">Close</button>
      </div>
    </div>
  </div>  
</template>

<style scoped>
.parking-spot {
  width: 40px;
  height: 40px;
  background-color: #4caf50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
  cursor: pointer;
}

</style>