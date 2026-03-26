<script setup>
    import ParkingSpot from '@/components/ParkingSpot.vue';

    import {ref} from 'vue';

    const props = defineProps(['parkinglot']);
    console.log("In parkinglotnew at top:",props.parkinglot);

    const emit = defineEmits(['edit_lot', 'delete_lot', 'add_spot', 'spot_deleted'])

    const editLot = () => {
        emit('edit_lot', props.parkinglot)
    }

    const deleteLot = () => {
        emit('delete_lot', props.parkinglot)
    }    

    const handleDeletedSpot = (pspot) =>{
        emit('spot_deleted', {lotId: props.parkinglot.id, spotId: pspot.spotid});
    }
</script>

<template>
        <div class="card d-inline-block" style="width: 350px; height: 290px; "> 
            <div class="card-header text-bg-primary text-white">
                Location: {{ props.parkinglot.id }} - {{ props.parkinglot.location }}                
            </div>
            <div class="card-body">
                <div class="row mb-2">
                    <div class="col">
                        <p class="mb-0">Price: &#8377;{{ props.parkinglot.price }}/hr</p>
                    </div>
                    <div class="col">
                        <p class="mb-0">#Pin: {{ props.parkinglot.pincode }}</p>
                    </div>
                </div>
                <div class="row row-cols-1 row-cols-sm-3 g-3" style="max-height: 170px; overflow-y: auto;">
                    <template v-if="props.parkinglot.spots && props.parkinglot.spots.length">
                        <ParkingSpot v-for="pspot in props.parkinglot.spots" :key="pspot.spotid" :parking-spot="pspot" @spot_deleted="handleDeletedSpot"/>
                    </template>
                    <template v-else>
                        <p>Loading spots...</p>  
                    </template>    
                </div>                
            </div>
            <div class="card-footer position-absolute bottom-0 end-0 start-0 d-flex justify-content-end gap-2">
                    <button class="btn btn-sm btn-outline-primary" style="font-size: 0.8rem; padding: 0.15rem 0.4rem;" @click="editLot">Edit Lot</button>
                    <button class="btn btn-sm btn-outline-danger" style="font-size: 0.8rem; padding: 0.15rem 0.4rem;" @click="deleteLot">Delete Lot</button>
            </div>
        </div>    
</template>