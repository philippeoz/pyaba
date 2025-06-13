<template>
  <div class="fullscreen bg-dark text-white text-center q-pa-md flex flex-center">
    <div class="error-container">

      <div class="error-number">
        <span class="four bounce-1">4</span>
        <span class="zero wiggle">0</span>
        <span class="four bounce-2">4</span>
      </div>

      <div class="emoji-container q-mt-md">
        <div class="emoji float">🤖</div>
      </div>

      <div class="text-h4 q-mt-md q-mb-sm main-message">
        Ops! Parece que você se perdeu...
      </div>

      <div class="text-body1 q-mt-md sub-message" style="opacity: 0.7; max-width: 500px; margin: 0 auto;">
        Ou este tutorial saiu para explorar novas fronteiras! 🚀
      </div>

      <div class="q-mt-xl column">
        <q-btn
          class="q-mb-md"
          color="primary"
          unelevated
          to="/"
          label="🏠 Voltar ao Início"
          no-caps
          size="lg"
        />
        <q-btn
          color="primary"
          unelevated
          @click="goBack"
          label="↩️ Voltar"
          no-caps
          size="lg"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
.error-container {
  max-width: 600px;
  margin: 0 auto;
}

.error-number {
  font-size: 20vh;
  font-weight: bold;
  font-family: 'Courier New', monospace;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.four, .zero {
  display: inline-block;
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
}

.bounce-1 {
  animation: bounce 2s ease-in-out infinite;
}

.bounce-2 {
  animation: bounce 2s ease-in-out infinite 0.5s;
}

.wiggle {
  animation: wiggle 3s ease-in-out infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-20px);
  }
  60% {
    transform: translateY(-10px);
  }
}

@keyframes wiggle {
  0%, 7% {
    transform: rotateZ(0);
  }
  15% {
    transform: rotateZ(-15deg);
  }
  20% {
    transform: rotateZ(10deg);
  }
  25% {
    transform: rotateZ(-10deg);
  }
  30% {
    transform: rotateZ(6deg);
  }
  35% {
    transform: rotateZ(-4deg);
  }
  40%, 100% {
    transform: rotateZ(0);
  }
}

.emoji-container {
  height: 80px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.emoji {
  font-size: 4rem;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.main-message {
  animation: fadeInUp 1s ease-out;
}

.sub-message {
  animation: fadeInUp 1s ease-out 0.3s both;
}

.button-container {
  animation: fadeInUp 1s ease-out 0.6s both;
}

.fun-fact {
  animation: fadeInUp 1s ease-out 0.9s both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}


.q-btn:hover {
  transform: translateY(-2px);
  transition: transform 0.3s ease;
}


@media (max-width: 600px) {
  .error-number {
    font-size: 15vh;
  }
  
  .emoji {
    font-size: 3rem;
  }
  
  .main-message {
    font-size: 1.5rem;
  }
  
  .button-container .q-btn {
    display: block;
    margin: 8px auto;
    width: 200px;
  }
}
</style>
