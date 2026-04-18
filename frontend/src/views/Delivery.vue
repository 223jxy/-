<template>
  <div class="delivery">
    <h2>配送管理</h2>
    
    <div class="delivery-tabs">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="我的配送" name="my-delivery">
          <el-table :data="myDeliveries" style="width: 100%">
            <el-table-column prop="id" label="配送编号" width="120"></el-table-column>
            <el-table-column prop="order_id" label="订单编号" width="120"></el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="pickup_location" label="取货地点"></el-table-column>
            <el-table-column prop="delivery_location" label="送达地点"></el-table-column>
            <el-table-column prop="estimated_time" label="预计送达时间"></el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" type="primary" @click="viewDelivery(scope.row.id)">查看</el-button>
                <el-button size="small" type="danger" @click="cancelDelivery(scope.row.id)" v-if="scope.row.status === 'PENDING'">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="配送员管理" name="delivery-person" v-if="isDeliveryPerson">
          <el-table :data="assignedDeliveries" style="width: 100%">
            <el-table-column prop="id" label="配送编号" width="120"></el-table-column>
            <el-table-column prop="order_id" label="订单编号" width="120"></el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="pickup_location" label="取货地点"></el-table-column>
            <el-table-column prop="delivery_location" label="送达地点"></el-table-column>
            <el-table-column prop="estimated_time" label="预计送达时间"></el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" type="primary" @click="updateStatus(scope.row.id, 'PICKED_UP')" v-if="scope.row.status === 'ASSIGNED'">已取货</el-button>
                <el-button size="small" type="success" @click="updateStatus(scope.row.id, 'DELIVERED')" v-if="scope.row.status === 'PICKED_UP'">已送达</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="创建配送" name="create-delivery">
          <el-form :model="deliveryForm" label-width="120px">
            <el-form-item label="订单编号">
              <el-input v-model="deliveryForm.order_id" placeholder="请输入订单编号"></el-input>
            </el-form-item>
            <el-form-item label="取货地点">
              <el-input v-model="deliveryForm.pickup_location" placeholder="请输入取货地点"></el-input>
            </el-form-item>
            <el-form-item label="送达地点">
              <el-input v-model="deliveryForm.delivery_location" placeholder="请输入送达地点"></el-input>
            </el-form-item>
            <el-form-item label="配送类型">
              <el-radio-group v-model="deliveryForm.is_express">
                <el-radio label="false">普通配送（24小时内）</el-radio>
                <el-radio label="true">加急配送（4小时内）</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="配送费">
              <el-input v-model.number="deliveryForm.fee" type="number" placeholder="请输入配送费"></el-input>
            </el-form-item>
            <el-form-item label="奖励金">
              <el-input v-model.number="deliveryForm.reward" type="number" placeholder="请输入奖励金"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="createDelivery">创建配送</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Delivery',
  data() {
    return {
      activeTab: 'my-delivery',
      isDeliveryPerson: true,
      deliveryForm: {
        order_id: '',
        pickup_location: '',
        delivery_location: '',
        is_express: false,
        fee: 5,
        reward: 3
      },
      myDeliveries: [
        {
          id: 1,
          order_id: 1,
          status: 'PENDING',
          pickup_location: '北京大学图书馆',
          delivery_location: '北京大学学生宿舍',
          estimated_time: '2026-03-31 10:30:00'
        },
        {
          id: 2,
          order_id: 2,
          status: 'DELIVERING',
          pickup_location: '清华大学图书馆',
          delivery_location: '清华大学学生宿舍',
          estimated_time: '2026-03-30 16:45:00'
        }
      ],
      assignedDeliveries: [
        {
          id: 3,
          order_id: 3,
          status: 'ASSIGNED',
          pickup_location: '北京大学图书馆',
          delivery_location: '北京大学学生宿舍',
          estimated_time: '2026-03-31 10:30:00'
        }
      ]
    }
  },
  methods: {
    getStatusText(status) {
      const statusMap = {
        'PENDING': '待分配',
        'ASSIGNED': '已分配',
        'PICKED_UP': '已取货',
        'DELIVERED': '已送达',
        'CANCELLED': '已取消'
      }
      return statusMap[status] || status
    },
    getStatusType(status) {
      const typeMap = {
        'PENDING': 'info',
        'ASSIGNED': 'warning',
        'PICKED_UP': 'primary',
        'DELIVERED': 'success',
        'CANCELLED': 'danger'
      }
      return typeMap[status] || 'info'
    },
    viewDelivery(deliveryId) {
      this.$message.info(`查看配送详情：${deliveryId}`)
    },
    cancelDelivery(deliveryId) {
      this.$confirm('确定要取消此配送吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$message.success('配送取消成功')
      }).catch(() => {
        this.$message.info('已取消操作')
      })
    },
    updateStatus(deliveryId, status) {
      this.$message.success(`配送状态已更新为：${this.getStatusText(status)}`)
    },
    createDelivery() {
      this.$message.success('配送创建成功')
      this.resetForm()
    },
    resetForm() {
      this.deliveryForm = {
        order_id: '',
        pickup_location: '',
        delivery_location: '',
        is_express: false,
        fee: 5,
        reward: 3
      }
    }
  }
}
</script>

<style scoped>
.delivery {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.delivery h2 {
  margin-bottom: 30px;
  color: #333;
}

.delivery-tabs {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.el-form {
  max-width: 600px;
}
</style>