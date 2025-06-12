const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/EventsPage.vue') },
      { path: ':slug', component: () => import('pages/TutorialsPage.vue') },
      { path: 'confirmation/:uuid', component: () => import('pages/ConfirmationPage.vue') }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
