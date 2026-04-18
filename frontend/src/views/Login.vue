<template>
  <div class="login">
    <div class="login-form">
      <h2>用户登录</h2>
      <el-form :model="loginForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="login">登录</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { encryptText } from '../utils/encryption'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    login() {
      // 加密密码
      const encryptedPassword = encryptText(this.loginForm.password)
      
      // 模拟登录请求
      this.$axios.post('/users/login', {
        username: this.loginForm.username,
        password: encryptedPassword
      })
      .then(response => {
        this.$message.success('登录成功')
        this.$router.push('/')
      })
      .catch(error => {
        this.$message.error('登录失败')
      })
    },
    resetForm() {
      this.loginForm = {
        username: '',
        password: ''
      }
    }
  }
}
</script>

<style scoped>
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f5f5f5;
}

.login-form {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.login-form h2 {
  margin-bottom: 30px;
  color: #333;
  text-align: center;
}
</style>