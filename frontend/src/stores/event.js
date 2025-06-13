import { defineStore } from 'pinia'
import { api } from '../boot/axios'
import { date } from 'quasar'

export const useEventStore = defineStore('event', {
  state: () => ({
    eventsLoading: true,
    tutorialsLoading: true,
    events: [],
    selectedEvent: null,
    loadingMessages: [
      // Mensagens de loading geradas carinhosamente pelo chat gpt 🤣
      "🥹 É lento, mas é honesto...",
      "🐢 Está lento, mas foi feito com carinho...",
      "💾 Carregando... porque o rápido era pago.",
      "🔌 A API levantou pra tomar um café.",
      "🐌 Devagar e sempre... ou só devagar mesmo.",
      "🤡 Os dados estão vindo. Juro.",
      "🔄 Pode demorar, mas olha que layout bonito.",
      "🧘 Respira. Medita. A resposta vem.",
      "🛠️ Se não fosse pela gambiarra, nem isso carregava.",
      "📡 Enviando sinais de fumaça pro servidor.",
      "🧃 Os dados foram comprar um suco. Já voltam.",
      "🐒 Um estagiário foi buscar a resposta manualmente.",
      "💡 Às vezes, o loading é o destino.",
      "💤 Enquanto carrega, tire um cochilo. Você merece.",
      "🫠 Temos fé que vai.",
      "🧊 Carregando na temperatura ambiente... do Ártico.",
      "🫥 Quase lá. Quer dizer... talvez.",
      "🧃 Um dev chorou pra fazer isso. Valorize.",
      "🧯 Carregando devagar pra não sobrecarregar o servidor da firma.",
      "🛳️ Está vindo... de navio... a remo.",
    ]
  }),

  getters: {
    getRandomLoadingMessage(state) {
      return state.loadingMessages[Math.floor(Math.random() * state.loadingMessages.length)]
    },
    selectedEventTurorials(state) {
      const tutorials = state.selectedEvent && state.selectedEvent.tutorials || []
      const groups = {}

      tutorials.map(tutorial => {
        const startDateOject = new Date(tutorial.start_datetime)
        const endDateOject = new Date(tutorial.end_datetime)
        const startDateString = date.formatDate(startDateOject, "DD/MM/YYYY")
        const hourStart = date.formatDate(startDateOject, "HH:mm")
        const hourEnd = date.formatDate(endDateOject, "HH:mm")
        const datetimeString = `${startDateString} das ${hourStart} às ${hourEnd}`

        tutorial.slots = tutorial.vacancies - tutorial.subscriptions

        if (!groups[datetimeString]) {
          groups[datetimeString] = []
        }
        groups[datetimeString].push(tutorial)
      })

      Object.values(groups).forEach(values => {
        values.sort((a, b) => a.title.localeCompare(b.title))
      })

      const orderedResult = {}
      Object.keys(groups)
        .sort((a, b) => {
          const parse = str => {
            const [day, month, yearHour] = str.split('/')
            const [year, hour] = yearHour.split(' às ')
            return new Date(`${year}-${month}-${day}T${hour}:00`)
          }
          return parse(a) - parse(b)
        })
        .forEach(chave => {
          orderedResult[chave] = groups[chave]
        })

      return orderedResult
    }
  },

  actions: {
    selectEvent(event) {
      this.selectedEvent = event
    },
    async fetchEvents() {
      this.eventsLoading = true
      try {
        const response = await api.get('/events/')
        this.events = response.data
        this.eventsLoading = false
      } catch (error) {
        console.error('Error fetching events:', error)
      }
    },
    fetchEventBySlug(slug) {
      return api.get(`/events/${slug}`)  
    },
    checkSubscription(tutorialId, cpf) {
      return api.post(`/tutorials/check_subscription/`, {
        cpf: cpf,
        tutorial_id: tutorialId
      })
    },
    subscribe(tutorialId, attendeeData) {
      return api.post(`/tutorials/${tutorialId}/subscribe/`, attendeeData)
    },
    unsubscribe(tutorialId, cpf) {
      return api.post(`/tutorials/${tutorialId}/unsubscribe/`, { cpf })
    },
    confirmSubscription(uuid) {
      return api.post(`/tutorials/confirm_subscription/`, { uuid })
    }
  }
})
