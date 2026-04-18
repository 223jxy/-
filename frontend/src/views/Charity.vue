<template>
  <div class="charity">
    <h2>公益联动</h2>
    
    <div class="charity-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="书籍捐赠" name="donate">
          <el-form :model="donateForm" label-width="120px">
            <el-form-item label="图书名称">
              <el-input v-model="donateForm.book_title" placeholder="请输入图书名称"></el-input>
            </el-form-item>
            <el-form-item label="数量">
              <el-input v-model.number="donateForm.quantity" type="number" placeholder="请输入捐赠数量"></el-input>
            </el-form-item>
            <el-form-item label="捐赠目的地">
              <el-select v-model="donateForm.destination" placeholder="请选择捐赠目的地">
                <el-option label="乡村小学书香驿站" value="乡村小学书香驿站"></el-option>
                <el-option label="贫困地区图书馆" value="贫困地区图书馆"></el-option>
                <el-option label="其他" value="其他"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="志愿时长">
              <el-input v-model.number="donateForm.volunteer_hours" type="number" placeholder="请输入志愿时长（小时）"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="donateBooks">捐赠图书</el-button>
              <el-button @click="resetDonateForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="线上支教" name="teach">
          <el-form :model="teachForm" label-width="120px">
            <el-form-item label="课程名称">
              <el-input v-model="teachForm.course" placeholder="请输入课程名称"></el-input>
            </el-form-item>
            <el-form-item label="支教时长">
              <el-input v-model.number="teachForm.hours" type="number" placeholder="请输入支教时长（小时）"></el-input>
            </el-form-item>
            <el-form-item label="支教对象">
              <el-select v-model="teachForm.target" placeholder="请选择支教对象">
                <el-option label="乡村小学" value="乡村小学"></el-option>
                <el-option label="贫困地区中学" value="贫困地区中学"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="volunteerTeach">报名支教</el-button>
              <el-button @click="resetTeachForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="捐赠记录" name="records">
          <el-table :data="donateRecords" style="width: 100%">
            <el-table-column prop="id" label="捐赠编号" width="120"></el-table-column>
            <el-table-column prop="book_title" label="图书名称"></el-table-column>
            <el-table-column prop="quantity" label="数量" width="100"></el-table-column>
            <el-table-column prop="destination" label="捐赠目的地"></el-table-column>
            <el-table-column prop="volunteer_hours" label="志愿时长" width="120"></el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="捐赠时间"></el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="公益合伙人" name="partner">
          <div class="partner-card">
            <h3>公益合伙人计划</h3>
            <p>累计捐赠50本书，即可成为公益合伙人，享受平台专属权益</p>
            <div class="partner-progress">
              <el-progress :percentage="partnerProgress" :format="formatProgress"></el-progress>
              <p class="progress-text">已捐赠 {{ totalBooks }} 本，还需 {{ remainingBooks }} 本</p>
            </div>
            <div class="partner-benefits" v-if="isPartner">
              <h4>合伙人权益</h4>
              <ul>
                <li>平台专属标识</li>
                <li>优先参与公益活动</li>
                <li>专属客服通道</li>
                <li>积分兑换折扣</li>
              </ul>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Charity',
  data() {
    return {
      activeTab: 'donate',
      donateForm: {
        book_title: '',
        quantity: 1,
        destination: '',
        volunteer_hours: 0
      },
      teachForm: {
        course: '',
        hours: 2,
        target: ''
      },
      donateRecords: [
        {
          id: 1,
          book_title: '高等数学',
          quantity: 2,
          destination: '乡村小学书香驿站',
          volunteer_hours: 2,
          status: '已完成',
          created_at: '2026-03-28 10:30:00'
        },
        {
          id: 2,
          book_title: '大学物理',
          quantity: 3,
          destination: '贫困地区图书馆',
          volunteer_hours: 3,
          status: '已完成',
          created_at: '2026-03-25 14:20:00'
        }
      ],
      totalBooks: 15,
      remainingBooks: 35,
      isPartner: false
    }
  },
  computed: {
    partnerProgress() {
      return Math.min(Math.round((this.totalBooks / 50) * 100), 100)
    }
  },
  methods: {
    getStatusType(status) {
      const typeMap = {
        '待处理': 'info',
        '已完成': 'success',
        '已取消': 'danger'
      }
      return typeMap[status] || 'info'
    },
    formatProgress(percentage) {
      return `${percentage}%`
    },
    donateBooks() {
      this.$message.success('图书捐赠成功，获得碳积分：' + (this.donateForm.quantity * 10))
      this.resetDonateForm()
    },
    resetDonateForm() {
      this.donateForm = {
        book_title: '',
        quantity: 1,
        destination: '',
        volunteer_hours: 0
      }
    },
    volunteerTeach() {
      this.$message.success('线上支教报名成功，志愿时长：' + this.teachForm.hours + '小时')
      this.resetTeachForm()
    },
    resetTeachForm() {
      this.teachForm = {
        course: '',
        hours: 2,
        target: ''
      }
    }
  }
}
</script>

<style scoped>
.charity {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.charity h2 {
  margin-bottom: 30px;
  color: #333;
}

.charity-tabs {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.el-form {
  max-width: 600px;
}

.partner-card {
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  color: white;
  text-align: center;
}

.partner-card h3 {
  margin-bottom: 20px;
  font-size: 1.5rem;
}

.partner-card p {
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.partner-progress {
  margin-bottom: 30px;
}

.progress-text {
  margin-top: 10px;
  font-size: 1rem;
}

.partner-benefits {
  background: rgba(255, 255, 255, 0.2);
  padding: 20px;
  border-radius: 10px;
  text-align: left;
}

.partner-benefits h4 {
  margin-bottom: 15px;
  font-size: 1.2rem;
}

.partner-benefits ul {
  list-style: none;
  padding: 0;
}

.partner-benefits li {
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.partner-benefits li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #4ecdc4;
  font-weight: bold;
}
</style>