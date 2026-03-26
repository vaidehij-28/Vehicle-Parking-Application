import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useMessageStore = defineStore('messageStore', () => {
  const errorMessages = ref('')
 
  function updateErrorMsgs(message) {
    errorMessages.value = message;
    setTimeout(() => {
       errorMessages.value = '' 
    }, 500);

  }

  return { errorMessages, updateErrorMsgs }
})
