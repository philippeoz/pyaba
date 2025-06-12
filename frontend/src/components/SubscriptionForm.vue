<template>
  <div class="row justify-center items-center">
    <q-input
      class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
      outline
      color="white"
      v-model="cpf"
      label="CPF"
      mask="###.###.###-##"
      hint="Informe seu CPF para realizar ou cancelar sua inscrição"
      :rules="[val => val.length != 11 || !!checkCPF(val) || 'CPF inválido']"
      :disable="cpfLoading"
      :loading="cpfLoading"
      ref="cpfRef"
      debounce="300"
    />
  </div>

  <template v-if="subscriptionData">
    <template
      v-if="subscriptionData.subscribed === false && subscriptionData.registration_id !== undefined"
    >
      <div class="text-h7 text-center q-mt-md">
        Você já está inscrito neste tutorial, mas ainda não confirmou sua presença.
      </div>
      <div class="text-h7 text-center q-mt-sm">
        Verifique seu email e confirme sua presença clicando no link enviado.
      </div>
    </template>
    <template
      v-if="subscriptionData && subscriptionData.subscribed === false && subscriptionData.registration_id === undefined"
    >
      <div class="row justify-center items-center" v-if="showUserForm">
        <q-input
          class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
          color="white"
          v-model="name"
          label="Nome Completo"
          ref="nameRef"
        />
      </div>
      <div class="row justify-center items-center" v-if="showUserForm">
        <q-input
          class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
          color="white"
          v-model="email"
          label="Email"
          ref="emailRef"
        />
      </div>
      <div class="row justify-center items-center" v-if="showUserForm">
        <q-input
          class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
          v-model="birthDate"
          color="white"
          label="Data de Nascimento"
          mask="##/##/####"
          ref="birthDateRef"
        >
          <template v-slot:append>
            <q-icon name="event" class="cursor-pointer">
              <q-popup-proxy cover transition-show="scale" transition-hide="scale">
                <q-date v-model="birthDate" mask="DD/MM/YYYY" locale="pt-BR">
                  <div class="row items-center justify-end">
                    <q-btn v-close-popup label="Close" color="primary" flat />
                  </div>
                </q-date>
              </q-popup-proxy>
            </q-icon>
          </template>
        </q-input>
      </div>
      <div class="row justify-center items-center q-mt-md" v-if="subscriptionData.available && !showUserForm">
        <q-btn
          class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
          color="secondary"
          @click="showUserForm = !showUserForm"
          :disable="subscriptionLoading"
        >
          Atualizar Cadastro
        </q-btn>
      </div>
      <div class="row justify-center items-center q-mt-md">
        <q-btn
          class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
          color="secondary" @click="handleSubscription"
          :disable="subscriptionLoading"
        >
          Realizar Inscrição
        </q-btn>
      </div>
    </template>
    <template
      v-if="subscriptionData.subscribed === true && !!subscriptionData.registration_id"
    >
      <div class="text-h7 text-center q-mt-md">
        Você está inscrito neste tutorial e confirmou sua presença.
      </div>
    </template>
    <template v-if="!!subscriptionData.registration_id">
      <div class="row justify-center items-center q-mt-md">
        <q-btn
          class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
          color="secondary"
          v-model="cancelDoubleCheck"
          @click="cancelDoubleCheck = !cancelDoubleCheck"
          v-if="!cancelDoubleCheck"
        >
          Cancelar Inscrição? 🥹
        </q-btn>
      </div>
      <div class="text-h7 text-center" v-if="cancelDoubleCheck">
        Tem certeza? 👀
      </div>
      <div class="row justify-center items-center q-mt-md">
        <q-btn
          class="col-4 col-sm-6 col-md-4 col-lg-3 col-xs-12 col-xl-2"
          color="secondary"
          v-model="cancelDoubleCheck"
          @click="cancelSubscription"
          v-if="cancelDoubleCheck"
        >
          Sim, pode cancelar 😢
        </q-btn>
      </div>
    </template>
  </template>
  <q-inner-loading :showing="subscriptionLoading">
    <q-spinner-hearts size="60px" color="red-5" />
  </q-inner-loading>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { isValidCPF } from 'boot/utils'
import { useEventStore } from 'stores/event'
import { useQuasar } from 'quasar'

const $q = useQuasar()

// Props
const props = defineProps({
  tutorial: {
    type: Object,
    required: true
  },
  event: {
    type: Object,
    required: true
  }
})

// Store
const store = useEventStore()

// Refs
const cpf = ref('')
const cpfLoading = ref(false)
const cpfRef = ref(null)
const subscriptionData = ref(null)
const name = ref('')
const nameRef = ref(null)
const email = ref('')
const emailRef = ref(null)
const birthDate = ref('')
const birthDateRef = ref(null)
const subscriptionLoading = ref(false)
const cancelDoubleCheck = ref(false)
const showUserForm = ref(true)

// Foca o input ao montar
onMounted(() => {
  nextTick(() => {
    cpfRef.value?.focus()
  })
})

watch(cpf, (val) => {
  val = val.replace(/\D/g, '')
  subscriptionData.value = null
  cancelDoubleCheck.value = false
  if (val.length === 11 && checkCPF(val)) {
    cpfLoading.value = true
    store.checkSubscription(props.tutorial.id, val).then(response => {
      cpfLoading.value = false
      if (
          response.data.subscribed === false
          && response.data.registration_id === undefined
          && response.data.available === false
      ) {
        $q.notify({
          type: 'negative',
          message: 'Não é possível inscrever-se neste tutorial.',
          caption: 'O participante está inscrito em outro tutorial no mesmo horário.'
        })
        return
      }
      subscriptionData.value = response.data
      if (response.data.available === true) {
        showUserForm.value = false
      }
      if (response.data.subscribed === false && response.data.registration_id === undefined) {
        nextTick(() => {
          nameRef.value?.focus()
        })
      }
    }).catch(response => {
      cpfLoading.value = false
      console.log(response.error)
      $q.notify({
        type: 'negative',
        message: `Erro ao verificar inscrição: ${response.message}`
      })
    })
  }
})

function checkCPF(value) {
  return isValidCPF(value.replace(/\D/g, ''))
}

const cancelSubscription = async () => {
  if (!checkCPF(cpf.value.replace(/\D/g, ''))) {
    $q.notify({
      type: 'negative',
      message: 'CPF inválido. Por favor, verifique o CPF informado.'
    })
    return
  }
  subscriptionLoading.value = true
  try {
    await store.unsubscribe(props.tutorial.id, cpf.value.replace(/\D/g, ''))
    subscriptionLoading.value = false
    $q.notify({
      type: 'positive',
      message: 'Inscrição cancelada com sucesso!'
    })
    cpf.value = ''
    subscriptionData.value = null
    nextTick(() => {
      cpfRef.value?.focus()
    })
  } catch (error) {
    subscriptionLoading.value = false
    $q.notify({
      type: 'negative',
      message: `Erro ao cancelar inscrição: ${error?.response?.data?.error || error?.message}`
    })
  }
}

function handleSubscription() {
  if (
      showUserForm.value && (
        !name.value || !email.value || !birthDate.value || !cpf.value || !checkCPF(cpf.value.replace(/\D/g, ''))
      )
    ) {
    $q.notify({
      type: 'negative',
      message: 'Por favor, preencha todos os campos corretamente.'
    })
    return
  }

  subscriptionLoading.value = true
  store.subscribe(props.tutorial.id, {
    cpf: cpf.value.replace(/\D/g, ''),
    name: name.value,
    email: email.value,
    birthday: birthDate.value
  }).then(() => {
    subscriptionLoading.value = false
    $q.notify({
      type: 'positive',
      message: 'Inscrição realizada com sucesso!',
      caption: 'Verifique seu email e confirme sua presença clicando no link enviado.',
      progress: true,
      timeout: 5000,
    })
    cpf.value = ''
    name.value = ''
    email.value = ''
    birthDate.value = ''
    subscriptionData.value = null
    nextTick(() => {
      cpfRef.value?.focus()
    })
  }).catch(error => {
    subscriptionLoading.value = false
    $q.notify({
      type: 'negative',
      message: `Erro ao realizar inscrição: ${error?.response?.data?.error || error?.message}`
    })
  })
}
</script>
