<template>
  <div class="publish-book">
    <h2>发布图书</h2>
    <el-form :model="bookForm" :rules="rules" ref="bookForm" label-width="100px" class="publish-form">
      <!-- 基础信息 -->
      <el-form-item label="图书标题" prop="title">
        <el-input v-model="bookForm.title" placeholder="请输入图书标题" clearable></el-input>
      </el-form-item>
      <el-form-item label="作者" prop="author">
        <el-input v-model="bookForm.author" placeholder="请输入作者" clearable></el-input>
      </el-form-item>
      <el-form-item label="ISBN" prop="isbn">
        <el-input v-model="bookForm.isbn" placeholder="请输入ISBN" clearable></el-input>
        <el-button type="primary" @click="scanISBN" style="margin-top: 10px;">扫描ISBN</el-button>
      </el-form-item>
      <el-form-item label="原价" prop="original_price">
        <el-input v-model.number="bookForm.original_price" type="number" placeholder="请输入原价" clearable></el-input>
      </el-form-item>
      
      <!-- 图书状态 -->
      <el-form-item label="品相" prop="condition">
        <el-radio-group v-model="bookForm.condition" size="small">
          <el-radio label="A1">A1（九成新）</el-radio>
          <el-radio label="A2">A2（八五新）</el-radio>
          <el-radio label="B">B（八成新）</el-radio>
          <el-radio label="C">C（五成新以上）</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="分类" prop="category">
        <el-select v-model="bookForm.category" placeholder="请选择分类" clearable>
          <el-option label="教材" value="教材"></el-option>
          <el-option label="备考资料" value="备考资料"></el-option>
          <el-option label="课外读物" value="课外读物"></el-option>
          <el-option label="其他" value="其他"></el-option>
        </el-select>
      </el-form-item>
      
      <!-- 校园信息 -->
      <el-form-item label="学校" prop="university">
        <el-select v-model="bookForm.university" placeholder="请选择学校" clearable>
          <el-option label="北京大学" value="北京大学"></el-option>
          <el-option label="清华大学" value="清华大学"></el-option>
          <el-option label="复旦大学" value="复旦大学"></el-option>
          <el-option label="上海交通大学" value="上海交通大学"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="专业" prop="major">
        <el-select v-model="bookForm.major" placeholder="请选择专业" clearable>
          <el-option label="数学" value="数学"></el-option>
          <el-option label="物理" value="物理"></el-option>
          <el-option label="计算机" value="计算机"></el-option>
          <el-option label="化学" value="化学"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="年级" prop="grade">
        <el-select v-model="bookForm.grade" placeholder="请选择年级" clearable>
          <el-option label="大一" value="大一"></el-option>
          <el-option label="大二" value="大二"></el-option>
          <el-option label="大三" value="大三"></el-option>
          <el-option label="大四" value="大四"></el-option>
        </el-select>
      </el-form-item>
      
      <!-- 其他信息 -->
      <el-form-item label="描述" prop="description">
        <el-input type="textarea" v-model="bookForm.description" placeholder="请输入图书描述" rows="3"></el-input>
      </el-form-item>
      <el-form-item label="图书封面" prop="cover_image">
        <el-upload
          class="avatar-uploader"
          action="/api/books/upload-cover"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
        >
          <img v-if="imageUrl" :src="imageUrl" class="avatar">
          <i v-else class="el-icon-plus avatar-uploader-icon"></i>
        </el-upload>
        <div class="upload-tip">建议上传JPG/PNG格式图片，大小不超过2MB</div>
      </el-form-item>
      
      <!-- 操作按钮 -->
      <el-form-item>
        <el-button type="primary" @click="publishBook" :loading="loading">发布图书</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="$router.push('/book-trade')">返回</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { validateInput, sanitizeInput } from '../utils/xss'
import logger from '../utils/logger'

const router = useRouter()

// 表单数据
const bookForm = reactive({
  title: '',
  author: '',
  isbn: '',
  original_price: 0,
  condition: 'A1',
  category: '',
  university: '',
  major: '',
  grade: '',
  description: '',
  owner_id: 1 // 模拟用户ID
})

// 其他状态
const imageUrl = ref('')
const loading = ref(false)
const bookFormRef = ref(null)

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入图书标题', trigger: 'blur' },
    { min: 2, max: 50, message: '标题长度在2到50个字符之间', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者', trigger: 'blur' },
    { min: 1, max: 30, message: '作者名称长度在1到30个字符之间', trigger: 'blur' }
  ],
  isbn: [
    { required: true, message: '请输入ISBN', trigger: 'blur' },
    { pattern: /^\d{10,13}$/, message: 'ISBN格式不正确', trigger: 'blur' }
  ],
  original_price: [
    { required: true, message: '请输入原价', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' }
  ],
  condition: [
    { required: true, message: '请选择品相', trigger: 'change' }
  ],
  category: [
    { required: true, message: '请选择分类', trigger: 'change' }
  ],
  university: [
    { required: true, message: '请选择学校', trigger: 'change' }
  ],
  major: [
    { required: true, message: '请选择专业', trigger: 'change' }
  ],
  grade: [
    { required: true, message: '请选择年级', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入图书描述', trigger: 'blur' },
    { min: 10, message: '描述长度至少10个字符', trigger: 'blur' }
  ]
}

/**
 * 扫描ISBN
 */
const scanISBN = () => {
  // 模拟扫描ISBN功能
  ElMessage.info('请将ISBN条码对准摄像头')
  // 模拟识别结果
  loading.value = true
  setTimeout(() => {
    bookForm.isbn = '9787040494435'
    bookForm.title = '高等数学'
    bookForm.author = '同济大学数学系'
    bookForm.original_price = 39.9
    ElMessage.success('ISBN识别成功')
    loading.value = false
  }, 1000)
}

/**
 * 处理封面上传成功
 * @param {Object} res 响应结果
 * @param {File} file 上传的文件
 */
const handleAvatarSuccess = (res, file) => {
  imageUrl.value = URL.createObjectURL(file.raw)
  ElMessage.success('封面上传成功')
}

/**
 * 上传前验证
 * @param {File} file 上传的文件
 * @returns {boolean} 是否允许上传
 */
const beforeAvatarUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('上传头像图片只能是 JPG/PNG 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('上传头像图片大小不能超过 2MB!')
  }
  return isJPG && isLt2M
}

/**
 * 发布图书
 */
const publishBook = () => {
  // 表单验证
  bookFormRef.value.validate((valid) => {
    if (valid) {
      // 验证用户输入，防止XSS攻击
      if (!validateInput(bookForm.title) || 
          !validateInput(bookForm.author) || 
          !validateInput(bookForm.description)) {
        ElMessage.error('输入内容包含不安全的字符，请检查后重试')
        return
      }
      
      // 清理用户输入
      bookForm.title = sanitizeInput(bookForm.title)
      bookForm.author = sanitizeInput(bookForm.author)
      bookForm.description = sanitizeInput(bookForm.description)
      
      // 模拟发布图书
      loading.value = true
      setTimeout(() => {
        ElMessage.success('图书发布成功')
        loading.value = false
        router.push('/book-trade')
      }, 1000)
    } else {
      ElMessage.error('请检查表单填写是否完整')
      return false
    }
  })
}

/**
 * 重置表单
 */
const resetForm = () => {
  bookFormRef.value.resetFields()
  imageUrl.value = ''
}
</script>

<style scoped>
.publish-book {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.publish-book h2 {
  margin-bottom: 30px;
  color: #333;
  text-align: center;
  font-size: 1.8rem;
  font-weight: bold;
}

.publish-form {
  background: #f9f9f9;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.2);
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
  border-radius: 6px;
  object-fit: cover;
}

.upload-tip {
  margin-top: 10px;
  font-size: 0.8rem;
  color: #999;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .publish-book {
    padding: 10px;
  }
  
  .publish-form {
    padding: 20px;
  }
  
  .el-form-item {
    margin-bottom: 15px;
  }
  
  .el-form-item__label {
    font-size: 0.9rem;
  }
  
  .el-input, .el-select, .el-textarea {
    width: 100%;
  }
  
  .el-radio-group {
    display: flex;
    flex-wrap: wrap;
  }
  
  .el-radio {
    margin-right: 15px;
    margin-bottom: 10px;
  }
}

@media (max-width: 480px) {
  .publish-book h2 {
    font-size: 1.5rem;
  }
  
  .publish-form {
    padding: 15px;
  }
  
  .el-form-item__label {
    font-size: 0.8rem;
  }
  
  .avatar-uploader-icon {
    width: 120px;
    height: 120px;
    line-height: 120px;
  }
  
  .avatar {
    width: 120px;
    height: 120px;
  }
}
</style>