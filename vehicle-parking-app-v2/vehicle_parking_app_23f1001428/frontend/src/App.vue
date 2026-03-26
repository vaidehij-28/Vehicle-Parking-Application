<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { useMessageStore } from '@/stores/messagestore.js';
import { useAuthStore } from '@/stores/authstore.js';
import { computed } from 'vue'
import { useRouter } from 'vue-router';

const router = useRouter();

const message_store = useMessageStore();
const auth_store = useAuthStore();

const ErrorMessages = computed(() => {
  return message_store.errorMessages;
})
const username = computed(()=>{
  return auth_store.getUserName();
})

async function logout(){
  //send a fetch request to backend to log out user
  const token = auth_store.getAuthToken()
  const response = await fetch("http://127.0.0.1:5000/api/logout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "authentication-token": token
    },
  });

  if (!response.ok){
    const errorData = await response.json();
    console.error(errorData);
    alert(`Logout failed: ${errorData.message}`);
    return;
   } else {
    auth_store.removeUserDetails();
    message_store.updateErrorMsgs("You have been logged out successfully");  
    router.push('/');                   
  }  
}

function goToSummary() {
  router.push('/summary')
}

</script>

<template>
  <div class="container">
    <nav class="navbar navbar-expand-lg bg-primary py-1" data-bs-theme="dark"> 
      <div class="container-fluid">
        <div class="d-flex align-items-center" >
          <span class="navbar-text fw-semibold fs-5" v-if="auth_store.isAuthenticated">
            <p class="nav-link active" aria-current="page"><img src="./assets/applogo.svg" alt="Logo" width="30" height="24" class="d-inline-block align-text-top">Welcome, {{ username }}</p>
          </span>
        </div>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
           <ul class="navbar-nav ms-auto">   
            <li class="nav-item mx-3" v-if="auth_store.isAuthenticated  && auth_store.getUserRole() == 'admin'">
              <RouterLink class="nav-link active" aria-current="page" to="/adminboard">Dashboard</RouterLink>
            </li>
             <li class="nav-item mx-3" v-if="auth_store.isAuthenticated  && auth_store.getUserRole() == 'user'">
              <RouterLink class="nav-link active" aria-current="page" to="/userboard">Dashboard</RouterLink>
            </li>
            <li class="nav-item mx-2" v-if="auth_store.isAuthenticated && auth_store.getUserRole() == 'admin'">
              <RouterLink class="nav-link active" aria-current="page" to="/adminboard/users">Users</RouterLink>
            </li>
            <li class="nav-item mx-2" v-if="auth_store.isAuthenticated && auth_store.getUserRole() == 'admin'">
              <a class="nav-link active" aria-current="page" @click.prevent="goToSummary">Summary</a>
            </li>
             <li class="nav-item mx-2" v-if="auth_store.isAuthenticated && auth_store.getUserRole() == 'user'">
              <a class="nav-link active" aria-current="page" @click.prevent="goToSummary">Summary</a>
            </li>
            <li class="nav-item mx-2" v-if="auth_store.isAuthenticated">
              <a class="nav-link active" aria-current="page" @click="logout"><img src="./assets/power.svg" alt="Logo" width="30" height="24" class="d-inline-block align-text-top">Logout</a>
            </li>  
          </ul>    
          <ul class="navbar-nav ms-auto">   
            <li class="nav-item mx-2" v-if="!auth_store.isAuthenticated">
              <RouterLink class="nav-link active" aria-current="page" to="/login"><img src="./assets/box-arrow-in-right.svg" alt="Logo" width="30" height="24" class="d-inline-block align-text-top">Login</RouterLink>
            </li>
            <li class="nav-item mx-2" v-if="!auth_store.isAuthenticated">
              <RouterLink class="nav-link active" aria-current="page" to="/register"><img src="./assets/person-plus.svg" alt="Logo" width="30" height="24" class="d-inline-block align-text-top">Register</RouterLink>
            </li>
          </ul>
          <!--form class="d-flex" role="search">
            <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search"/>
            <button class="btn btn-outline-success" type="submit">Search</button>
          </form>-->
        </div>
        <div class="collapse navbar-collapse" id="navbarSupportedContent" v-if="auth_store.isAuthenticated">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item mx-3" v-if="auth_store.isAuthenticated  && auth_store.getUserRole() == 'user'">
              <RouterLink class="nav-link active" aria-current="page" to="/profile">Edit Profile</RouterLink>
            </li>            
          </ul>     
        </div>
      </div>
    </nav>

    <div class="container-fluid">
      <p class="text-center mt-3" v-if="ErrorMessages">{{  ErrorMessages }}</p> 
    </div>
 
    <RouterView/>
   
  </div>
</template>


