import { createStore } from 'vuex'

export default createStore({
  state: {
    user: null,
    books: [],
    selectedBook: null,
    carbonPoints: 0,
    orders: []
  },
  mutations: {
    setUser(state, user) {
      state.user = user
    },
    setBooks(state, books) {
      state.books = books
    },
    setSelectedBook(state, book) {
      state.selectedBook = book
    },
    setCarbonPoints(state, points) {
      state.carbonPoints = points
    },
    addOrder(state, order) {
      state.orders.push(order)
    }
  },
  actions: {
    async fetchBooks({ commit }) {
      // 模拟API调用
      const mockBooks = [
        {
          id: 1,
          title: '高等数学',
          author: '同济大学数学系',
          isbn: '9787040494435',
          price: 39.9,
          condition: 'A1',
          category: '教材',
          university: '北京大学',
          major: '数学',
          grade: '大一'
        },
        {
          id: 2,
          title: '大学物理',
          author: '张三',
          isbn: '9787040501735',
          price: 45.0,
          condition: 'A2',
          category: '教材',
          university: '清华大学',
          major: '物理',
          grade: '大二'
        }
      ]
      commit('setBooks', mockBooks)
    }
  },
  getters: {
    getUser: state => state.user,
    getBooks: state => state.books,
    getSelectedBook: state => state.selectedBook,
    getCarbonPoints: state => state.carbonPoints,
    getOrders: state => state.orders
  }
})