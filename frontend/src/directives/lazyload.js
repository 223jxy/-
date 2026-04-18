// 图片懒加载指令
const lazyload = {
  mounted(el, binding) {
    const options = {
      root: null,
      rootMargin: '0px',
      threshold: 0.1
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target
          img.src = binding.value
          observer.unobserve(img)
        }
      })
    }, options)

    observer.observe(el)
  }
}

export default lazyload