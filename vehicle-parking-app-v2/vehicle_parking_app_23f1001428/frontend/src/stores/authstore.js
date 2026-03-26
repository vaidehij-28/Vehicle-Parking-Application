import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('authStore', () => {
    const authToken = ref(localStorage.getItem('token') || null)
    const isAuthenticated = computed(() => authToken.value != null)
    const user = ref(JSON.parse(localStorage.getItem('user') || null))

    function setUserDetails(token, userdata){
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(userdata))
        authToken.value = token
        user.value = userdata
    }

    function removeUserDetails(){
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        authToken.value = null
        user.value = null
    }
 
    function getAuthToken(){
        return authToken.value;
    }

    function getUserName(){
        return user.value ? user.value.username : null
    }

    function getUserid(){
        return user.value ? user.value.userid : null
    }

    function getUserRole(){
        return user.value ? user.value.roles : []
    }


    return { isAuthenticated, getAuthToken, setUserDetails, getUserName, getUserid, getUserRole, removeUserDetails }
})
