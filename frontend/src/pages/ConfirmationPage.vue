<template>
  <q-page class="flex flex-center q-pa-md column items-start">
    <template v-if="subscriptionData && subscriptionData?.confirmed == true">
      <p class="text-h6">
        🎉 Parabéns! 🎉
      </p>
      <p class="text-h7 q-mb-0 q-pb-0">
        Sua inscrição foi confirmada e sua vaga está garantida no tutorial:
      </p>
      <p class="text-h7">
        <strong>{{ subscriptionData?.tutorial_title }}</strong>
      </p>
      <p class="text-h7">
        que acontecerá no evento <strong>{{ subscriptionData?.event_title }}</strong>
      </p>
      <p>
        <q-img width="300px" src="~/assets/minions.gif" />
      </p>
      <q-btn color="secondary" :to="`/${subscriptionData?.event_slug}`">
        Voltar para tutoriais
      </q-btn>
    </template>
    <template v-if="subscriptionData && subscriptionData?.confirmed == false">
      <p class="text-h6">
        😔 Ops! As vagas se esgotaram.
      </p>
      <p class="text-h7 q-mb-0 q-pb-0">
        Infelizmente você não conseguiu confirmar sua inscrição a tempo.
      </p>
      <p class="text-h7">
        O tutorial <strong>{{ subscriptionData?.tutorial_title }}</strong> já está com todas as vagas preenchidas.
      </p>
      <p class="text-h7">
        Mas não desanime! Ainda dá tempo de participar de outros tutoriais no evento <strong>{{ subscriptionData?.event_title }}</strong>.
      </p>
      <q-img width="300px" src="~/assets/sad-minions.gif" />
      <q-btn color="secondary" class="q-mt-md" :to="`/${subscriptionData?.event_slug}`">
        Ver outros tutoriais
      </q-btn>
    </template>
  </q-page>
  <q-inner-loading :showing="confirmationLoading">
    <q-spinner-hearts size="60px" color="red-5" />
    {{ store.getRandomLoadingMessage }}
  </q-inner-loading>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useEventStore } from 'stores/event';
import { useRoute } from 'vue-router'

const store = useEventStore()
const route = useRoute()
const confirmationLoading = ref(false)
const subscriptionData = ref(null)
const errorMessage = ref(store.getRandomLoadingMessage)

onMounted(() => {
  const uuid = route?.params?.uuid
  if (uuid) {
    store.confirmSubscription(uuid).then(response => {
      subscriptionData.value = response.data
    }).catch(error => {
      console.log(error)
      errorMessage.value = true
    })
  }
})
</script>
