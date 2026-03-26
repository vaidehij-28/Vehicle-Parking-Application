<script setup>
    import { ref, onMounted } from 'vue'
    import { useAuthStore } from '@/stores/authstore.js';

    const auth_store = useAuthStore();
    const profile = ref({
        username: '',
        fullname: '',
        address: '',
        pincode: ''
    })
    const message = ref('')
    const loading = ref(true)

    onMounted(async () => {
        try {      
            const token = auth_store.getAuthToken()
            const userid = auth_store.getUserid()
            const response = await fetch(`http://127.0.0.1:5000/api/users/${userid}`, {
                method: "GET",           
                headers: {
                    "authentication-token": token
                }
            })
            if (!response.ok) {
                throw new Error('failed while fetching user details')
            }
            const data = await response.json()
            if (data.user_details){
                profile.value ={
                    username: data.user_details.username,
                    fullname: data.user_details.fullname,
                    address: data.user_details.address,
                    pincode: data.user_details.pincode,
                } 
            } else {
                console.error('user details missing in response', data)
            }  
            loading.value = false         
        } catch (error) {
            console.error('Failed to fetch lots:', error)
        }
    })

    const updateProfile = async () => {
        try {
            const token = auth_store.getAuthToken()
            const res = await fetch('http://127.0.0.1:5000/api/users', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'authentication-token': token
                },
                body: JSON.stringify({
                    fullname: profile.value.fullname,
                    address: profile.value.address,
                    pincode: profile.value.pincode
                })
            })
            const data = await res.json()
            message.value = data.message || 'Profile updated!'
        } catch (err) {
            console.error('Failed to update profile:', err)
            message.value = 'Failed to update profile.'
        }
    }
</script>

<template>
    <div class="container mt-4">
    <h3>User Profile</h3>

    <div v-if="loading">Loading...</div>

    <form v-else @submit.prevent="updateProfile">
      <div class="mb-3">
        <label>Username (read-only)</label>
        <input class="form-control" v-model="profile.username" disabled />
      </div>
      <div class="mb-3">
        <label>Full Name</label>
        <input class="form-control" v-model="profile.fullname" />
      </div>
      <div class="mb-3">
        <label>Address</label>
        <input class="form-control" v-model="profile.address" />
      </div>
      <div class="mb-3">
        <label>Pincode</label>
        <input class="form-control" v-model="profile.pincode" />
      </div>

      <button type="submit" class="btn btn-primary">Save</button>
    </form>

    <div v-if="message" class="alert alert-info mt-3">
      {{ message }}
    </div>
  </div>    
</template>   