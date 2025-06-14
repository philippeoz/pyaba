<template>
  <q-layout view="lHh Lpr lFf">
    <q-header>
      <q-toolbar>
        <q-breadcrumbs active-color="white" style="font-size: 16px">
          <template v-slot:separator>
            <q-icon
              size="1.2em"
              name="arrow_forward"
            />
          </template>
          <q-breadcrumbs-el label="Eventos" icon="assignment_ind" to="/"/>
          <q-breadcrumbs-el
            :label="store.selectedEvent.title"
            :to="`/${store.selectedEvent.slug}`"
            v-if="store.selectedEvent"
          />
          <q-breadcrumbs-el
            label="Tutoriais"
            v-if="store.selectedEvent"
          />
        </q-breadcrumbs>
      </q-toolbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
    <q-footer>
      <q-toolbar>
        <q-space></q-space>
        <q-btn flat no-caps rounded size="sm" href="https://github.com/philippeoz/pyaba" target="_blank">
          <code>
            {{ "{} with 💖 by @philippeoz" }}
          </code>
        </q-btn>
      </q-toolbar>
    </q-footer>
  </q-layout>
</template>

<script>
  import { useEventStore } from 'stores/event';

  export default {
    setup() {
      const store = useEventStore();
      return {
        store
      }
    }
  };
</script>
