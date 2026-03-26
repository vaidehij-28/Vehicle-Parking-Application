<template>
    <div class="container-fluid">
        <div class="row justify-content-center">
            <div class="col-6">
                <h1 class="col-6">Register</h1>
                <form @submit.prevent="registerUser">
                    <div class="mb-3">
                        <label for="inputEmail" class="form-label">Username(Email)</label>
                        <input type="email" class="form-control" id="inputEmail" aria-describedby="emailHelp" @input="validateEmail" v-model="username">
                        <p class="from-text" v-if="checkemailmsg">{{ checkemailmsg }}</p>
                    </div>
                    <div class="mb-3">
                        <label for="inputPassword" class="form-label">Password</label>
                        <input type="password" class="form-control" id="inputPassword" v-model="password" @input="validatePassword" >
                        <p class="from-text" v-if="passwordmsg">{{ passwordmsg }}</p>
                    </div>
                    <div class="mb-3">
                        <label for="inputFullname" class="form-label">Fullname</label>
                        <input type="text" class="form-control" id="inputFullname" v-model="fullname">
                    </div>
                    <div class="mb-3">
                        <label for="inputAddress" class="form-label">Address</label>
                        <input type="text" class="form-control" id="inputAddress" v-model="address">
                        </div>
                    <div class="mb-3">
                        <label for="inputPincode" class="form-label">Pincode</label>
                        <input type="text" class="form-control" id="inputPincode" v-model="pincode">
                    </div>                    
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            </div>
        </div>
    </div>
</template>    

<script setup>
    import { ref } from 'vue';
    import { useRouter } from 'vue-router';

    const router = useRouter();
     
    const username = ref('');
    const password = ref('')
    const fullname = ref('');
    const address = ref('')
    const pincode = ref('')
    const checkemailmsg = ref('')
    const passwordmsg = ref('')
    const isEmailAvailable = ref(false);

    async function validateEmail(){
        try{
            const response = await fetch('http://127.0.0.1:5000/api/checkemail', {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify({username: username.value})
            } );
            if (!response.ok){
                throw new Error("Email check failed")
            }
            
            const data = await response.json();
            isEmailAvailable.value = data.available;
            if (data.available){
                checkemailmsg.value = 'User name is avaialble';
            } else {            
                checkemailmsg.value = "User name is not available";
            }
        } catch(error){
            console.error("Error during emil checking:", error);
            checkemailmsg.value = 'Error while checking email availability';
            isEmailAvailable.value = false;
        }        
    }

    function validatePassword(){
        if (password.value.length < 8){
            passwordmsg.value = "Password must have at least 8 characters";   
            return false;           
        } else {
            passwordmsg.value='';
            return true;
        }

    }

    async function registerUser(){
        await validateEmail();
        if (username.value == '' || password.value == '' || fullname.value == '' || address.value == '' || pincode.value == ''){
            alert("Please fill all the values");
            return;
        }
        if (!validatePassword()){
            alert("Please enter a valid Password");
            return;
        }
        if (!isEmailAvailable.value){
            alert("Please enter a valid User name");
            return;
        }
        const registerdetails = {
            username: username.value,
            password: password.value,
            fullname: fullname.value,
            address: address .value,
            pincode: pincode.value
        }
        try{
            const response = await fetch("http://127.0.0.1:5000/api/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(registerdetails)
                
            });
            if (!response.ok){
                const errorData = await response.json();
                console.error(errorData);
                alert(`Registeration failed: ${errorData.message}`);
                return;
            }
            const resData = await response.json();
            alert(resData.message);
            router.push('/login')
        } catch(error){
            console.error('Registration error:', error);
            alert("Registration failed")
        }
    }
</script>