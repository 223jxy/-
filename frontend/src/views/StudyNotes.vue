<template>
  <div class="study-notes">
    <h2>学霸笔记专区</h2>
    
    <div class="notes-header">
      <el-input v-model="searchQuery" placeholder="搜索笔记" style="width: 300px; margin-right: 10px;"></el-input>
      <el-button type="primary" @click="searchNotes">搜索</el-button>
      <el-button type="success" @click="navigateToPublish" style="margin-left: 20px;">发布笔记</el-button>
    </div>
    
    <div class="notes-list">
      <div class="note-item" v-for="note in safeNotes" :key="note.id" @click="navigateToDetail(note.id)">
        <h3>{{ note.title }}</h3>
        <p class="note-author">作者：{{ note.author }}</p>
        <p class="note-preview">{{ note.content.substring(0, 100) }}...</p>
        <div class="note-meta">
          <span class="note-price">¥{{ note.price }}</span>
          <span class="note-stats">浏览 {{ note.views }} | 点赞 {{ note.likes }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { escapeHtml } from '../utils/xss'

export default {
  name: 'StudyNotes',
  data() {
    return {
      searchQuery: '',
      notes: [
        {
          id: 1,
          title: '高等数学上册知识点总结',
          author: '李四',
          content: '本笔记总结了高等数学上册的主要知识点，包括函数与极限、导数与微分、微分中值定理与导数的应用、不定积分等章节的重点内容和典型例题。',
          price: 19.9,
          views: 120,
          likes: 35
        },
        {
          id: 2,
          title: '大学物理实验报告模板',
          author: '王五',
          content: '本模板包含了大学物理实验报告的标准格式和写作方法，适用于各种物理实验课程。',
          price: 9.9,
          views: 85,
          likes: 20
        },
        {
          id: 3,
          title: '计算机网络复习资料',
          author: '赵六',
          content: '本资料涵盖了计算机网络的基本概念、OSI七层模型、TCP/IP协议栈、网络安全等内容，是期末考试的必备复习资料。',
          price: 29.9,
          views: 150,
          likes: 45
        }
      ]
    }
  },
  computed: {
    safeNotes() {
      return this.notes.map(note => ({
        ...note,
        title: escapeHtml(note.title),
        author: escapeHtml(note.author),
        content: escapeHtml(note.content)
      }))
    }
  },
  methods: {
    searchNotes() {
      // 模拟搜索功能
      const filteredNotes = this.notes.filter(note => {
        return note.title.includes(this.searchQuery) || note.content.includes(this.searchQuery)
      })
      this.notes = filteredNotes
    },
    navigateToPublish() {
      this.$message.info('发布笔记功能开发中')
    },
    navigateToDetail(noteId) {
      this.$message.info(`查看笔记详情：${noteId}`)
    }
  }
}
</script>

<style scoped>
.study-notes {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.study-notes h2 {
  margin-bottom: 30px;
  color: #333;
}

.notes-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.notes-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.note-item {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.note-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.note-item h3 {
  margin-bottom: 10px;
  color: #333;
  font-size: 1.1rem;
}

.note-author {
  margin-bottom: 10px;
  color: #666;
  font-size: 0.9rem;
}

.note-preview {
  margin-bottom: 15px;
  color: #999;
  font-size: 0.9rem;
  line-height: 1.4;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-price {
  color: #ff6b6b;
  font-weight: bold;
  font-size: 1.1rem;
}

.note-stats {
  color: #999;
  font-size: 0.8rem;
}
</style>