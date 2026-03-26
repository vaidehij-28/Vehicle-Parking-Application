<template>
    <div class="container-fluid">
        <div class="row justify-content-center">
            <div class="card mx-auto mt-5" style="max-width: 350px;">
                <div class="card-header bg-primary text-white text-center">    
                    <h4>ZippyPark</h4>
                    <p style="font-size: 0.8rem;">welcome back</p>
                </div>
                <form @submit.prevent="login">
                    <div class="mb-3">
                        <label for="inputEmail" class="form-label">Username(Email)</label>
                        <input type="email" class="form-control" id="inputEmail" aria-describedby="emailHelp" v-model="username">
                        <div id="emailHelp" class="form-text">We'll never share your email with anyone else.</div>
                    </div>
                    <div class="mb-3">
                        <label for="inputPassword" class="form-label">Password</label>
                        <input type="password" class="form-control" id="inputPassword" v-model="password" @input="validatePassword" >
                        <div id="passHelp" class="form-text">{{ passError }}</div>
                    </div>                    
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref } from 'vue';
    import { useMessageStore } from '@/stores/messagestore.js';
    import { useAuthStore } from '@/stores/authstore.js';
    import { useRouter } from 'vue-router';

    const router = useRouter();
    const message_store = useMessageStore();
    const auth_store = useAuthStore();

    const username = ref('');
    const password = ref('');
    const passError = ref('')

    const validatePassword = () => {
        if (password.value.length < 6){
            passError.value = 'Password must be at leas 6 character long.';
            return false;
        } else {
            passError.value = '';
            return true;
        }
    }

    async function login(){
        if (username.value == '' || password.value == ''){
            alert("Please fill all the values");
            return;
        }
        if (!validatePassword){
            alert("Invlid Password");
            return;
        } 
        const logindetails = {
            username: username.value,
            password: password.value
        }
        const response = await fetch("http://127.0.0.1:5000/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(logindetails)
            
        });
        if (!response.ok){
            const errorData = await response.json();
            console.error(errorData);
            alert(`Login failed: ${errorData.message}`);
            return;
        } else {
            const resData = await response.json();
            message_store .updateErrorMsgs(resData.message);
            const user = {
                userid: resData.user_details.userid,
                username : resData.user_details.username,
                roles : resData.user_details.roles 
            }
            try {
                auth_store.setUserDetails(resData.user_details.auth_token, user);
            } catch (e) {
                console.error('Error in setUserDetails:', e)
             }   

            let loginroles = resData.user_details.roles;
            if (loginroles.includes('admin')){
                router.push('/adminboard')
            } else {
                router.push('/userboard')
            }                
        }
    }
</script>