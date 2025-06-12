<template>
  <q-page class="flex flex-center q-pa-md row items-start q-gutter-md">
    <q-card class="my-card" flat bordered v-for="event in store.events" :key="event.id" :showing="!store.eventsLoading">
      <q-img :src="event.image_url" fit="fill" height="150px" />

      <q-card-section>
        <q-btn fab color="secondary" icon="web" class="absolute"
          style="top: 0; right: 12px; transform: translateY(-50%);"
          :href="event.url"
        >
          <q-tooltip anchor="top middle" self="bottom middle" :offset="[10, 10]">
            Site do evento
          </q-tooltip>
        </q-btn>
        <div class="row no-wrap items-center">
          <div class="col text-h6 ellipsis">
            {{ event.title }}
          </div>
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <div class="text-subtitle1">
          {{ event.description }}
        </div>
        <div class="text-caption text-grey">
          {{ event.location }}
        </div>
        <div class="text-caption text-grey">
          {{ event.start_date }} - {{ event.end_date }}
        </div>
      </q-card-section>

      <q-separator />

      <q-card-actions vertical>
        <q-btn color="secondary" class="full-width" :to="`/${event.slug}`" @click="store.selectEvent(event)">
          Tutoriais
          <q-tooltip>Inscreva-se!</q-tooltip>
        </q-btn>
      </q-card-actions>
    </q-card>
    <q-separator />
  </q-page>
  <q-inner-loading :showing="store.eventsLoading">
    <q-spinner-hearts size="60px" color="red-5" />
    {{ store.getRandomLoadingMessage }}
  </q-inner-loading>
</template>

<script setup>
import { onMounted } from 'vue'
import { useEventStore } from 'stores/event';

const store = useEventStore();

onMounted(() => {
  store.events = []
  store.selectedEvent = null
  store.fetchEvents()
})
</script>
