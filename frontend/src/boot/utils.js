import { defineBoot } from '#q-app/wrappers'

const isValidCPF = cpf => {
    cpf = cpf.replace(/[^\d]+/g, '')

    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false

    let sum = 0
    for (let i = 0; i < 9; i++) sum += parseInt(cpf[i]) * (10 - i)
    let firstCheck = (sum * 10) % 11
    if (firstCheck === 10 || firstCheck === 11) firstCheck = 0
    if (firstCheck !== parseInt(cpf[9])) return false

    sum = 0
    for (let i = 0; i < 10; i++) sum += parseInt(cpf[i]) * (11 - i)
    let secondCheck = (sum * 10) % 11
    if (secondCheck === 10 || secondCheck === 11) secondCheck = 0
    return secondCheck === parseInt(cpf[10])
};

export default defineBoot(({ app }) => {
    app.config.globalProperties.$utils = {
        isValidCPF
    }
})

export { isValidCPF }
