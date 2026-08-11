// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt({
  rules: {
    // Route files are named after their URL segment, which is single word by design.
    'vue/multi-word-component-names': 'off',
  },
})
