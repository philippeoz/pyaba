<template>
  <q-page class="flex q-pa-md row items-start content-start" :showing="!store.tutorialsLoading">
    <q-list
      bordered
      separator
      class="rounded-borders col-12 q-mb-md"
      v-for="(tutorials, dateString) in store.selectedEventTurorials" :key="dateString"
    >
      <q-item-label header>{{ dateString }}</q-item-label>

      <q-expansion-item v-for="tutorial in tutorials" :key="tutorial.id" group="tutorials">
        <template v-slot:header>
          <q-item-section middle>
            <q-item-label lines="3">{{ tutorial.title }}</q-item-label>
            <q-item-label caption class="text-grey-7">{{ tutorial.location }}</q-item-label>
            <q-item-label lines="1" v-if="$q.screen.lt.md">
              <q-chip color="secondary" v-for="instructor in tutorial.instructors" :key="instructor.id" size="12px">
                <q-avatar>
                  <q-img :src="instructor.photo_url" />
                </q-avatar>
                {{ instructor.name }}
              </q-chip>
            </q-item-label>
          </q-item-section>
          <q-item-section v-if="$q.screen.gt.sm">
            <q-item-label lines="1">
              <q-chip color="secondary" v-for="instructor in tutorial.instructors" :key="instructor.id" size="15px">
                <q-avatar>
                  <q-img :src="instructor.photo_url" />
                </q-avatar>
                {{ instructor.name }}
              </q-chip>
            </q-item-label>
          </q-item-section>
          <q-item-section middle side>
            <q-badge outline
              :color="tutorial.slots > 0 ? 'positive' : 'negative'"
              :label="tutorial.slots > 0 ? `${tutorial.slots} ${tutorial.slots > 1 ? 'vagas' : 'vaga'}` : 'Vagas esgotadas'"
            />
          </q-item-section>
        </template>

        <q-card>
          <q-tabs align="justify" v-model="tab" dense>
            <q-tab label="Descrição" name="one" />
            <q-tab label="Inscrição" name="two" />
          </q-tabs>
          <q-separator />
          <q-tab-panels v-model="tab">
            <q-tab-panel name="one">
              {{ tutorial.description }}
            </q-tab-panel>
            <q-tab-panel name="two">
              <subscription-form
                :tutorial="tutorial"
                :event="store.selectedEvent"
              />
            </q-tab-panel>
          </q-tab-panels>
        </q-card>

      </q-expansion-item>
    </q-list>
  </q-page>
  <q-inner-loading :showing="store.tutorialsLoading">
    <q-spinner-hearts size="60px" color="red-5" />
    {{ store.getRandomLoadingMessage }}
  </q-inner-loading>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useQuasar } from 'quasar'
import { useEventStore } from 'stores/event';
import { useRoute, useRouter } from 'vue-router'

import SubscriptionForm from 'components/SubscriptionForm.vue'

const store = useEventStore();
const router = useRouter()
const route = useRoute()
const $q = useQuasar()
const tab = ref('one')

onMounted(() => {
  store.tutorialsLoading = true
  store.fetchEventBySlug(route.params.slug).then(response => {
    store.selectedEvent = response.data
    store.tutorialsLoading = false
  }).catch(error => {
    console.log(error)

    $q.notify({
      type: 'negative',
      message: 'Ocorreu um erro ao tentar acessar esse vento, parece que ele não existe.',
      caption: 'Vou redirecionar você',
      timeout: 3000,
    })

    setTimeout(() => {
      router.push("/")
    }, 3000);

  })
})
</script>
