// https://v3.nuxtjs.org/api/configuration/nuxt.config
export default defineNuxtConfig({
  modules: [
    '@nuxt/content',
    '@nuxthq/ui',
  ],
  content: {
    sources: {
      charts: {
        driver: 'github',
        prefix: '/charts',
        repo: 'wearefrank/charts',
        branch: 'main',
        dir: 'charts'
      },
      index: {
        driver: 'github',
        prefix: '/charts',
        repo: 'wearefrank/charts',
        branch: 'gh-pages',
        dir: ''
      },
    },
    ignores: [
      '/templates/',
      '/docs/',
      '\\.svg$',
      '\\.lock$'
    ],
    highlight: {
      theme: 'github-light'
    },
  },
  colorMode: {
    preference: 'light'
  }
})

