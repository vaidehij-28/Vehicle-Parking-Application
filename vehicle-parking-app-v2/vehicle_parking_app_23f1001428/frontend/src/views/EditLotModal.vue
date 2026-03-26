<template>
  <div class="modal fade" ref="modalRef" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <form @submit.prevent="submitForm">
          <div class="modal-header">
            <h5 class="modal-title">Edit Lot</h5>
            <button type="button" class="btn-close" @click="hideModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">

                <label for="locName" class="form-label">Location Name</label>
                <input type="text" class="form-control" id="locName" v-model="locName" required/>
                <label for="Address" class="form-label">Address</label>
                <input type="text" class="form-control" id="address" v-model="address" required/>
                <div class="row mt-3">
                    <div class="col">
                    <label for="pincode" class="form-label">Pin Code</label>
                    <input type="text" class="form-control" id="pincode" v-model="pincode" required />
                    </div>
                    <div class="col">
                    <label for="price" class="form-label">Price per Hour</label>
                    <input type="text" class="form-control" id="price" v-model="price" required />
                    </div>
                </div>
                <label for="noofSpots" class="form-label">Number of Spots</label>
                <select id="noofSpots" class="form-select" v-model="noofSpots" required>
                    <option disabled value="">Select number of spots</option>
                    <option v-for="n in 50" :key="n" :value="n">{{ n }}</option>
                </select>              
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideModal">Cancel</button>
            <button type="submit" class="btn btn-primary">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
const emit = defineEmits(['edit_lot'])

const props = defineProps({
  lot: Object
})

const modalRef = ref(null)
let modalInstance = null

const locName = ref('')
const address = ref('')
const pincode = ref('')
const price = ref('')
const noofSpots = ref('')

watch(() => props.lot, (newVal) => {
  if (newVal) {
    locName.value = newVal.location || ''
    address.value = newVal.address || ''
    pincode.value = newVal.pincode || ''
    price.value = newVal.price || ''
    noofSpots.value = newVal.noofspots || ''
  }
})

const showModal = () => modalInstance?.show()
const hideModal = () => modalInstance?.hide()

const submitForm = () => {
  emit('edit_lot', {
    id: props.lot.id, 
    location: locName.value,
    address: address.value,
    pincode: pincode.value,
    price: price.value,
    noofspots: noofSpots.value
  })
  hideModal()
}

onMounted(() => {
  modalInstance = new window.bootstrap.Modal(modalRef.value)
})

defineExpose({ showModal, hideModal })
</script>
