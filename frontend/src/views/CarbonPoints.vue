<template>
  <div class="carbon-points">
    <div class="points-summary">
      <h2>碳积分账户</h2>
      <div class="points-card">
        <div class="points-amount">{{ carbonPoints }}</div>
        <div class="points-label">当前碳积分</div>
      </div>
    </div>
    
    <div class="points-history">
      <h3>积分历史</h3>
      <el-table :data="pointsHistory" style="width: 100%">
        <el-table-column prop="points" label="积分" width="120"></el-table-column>
        <el-table-column prop="source" label="来源"></el-table-column>
        <el-table-column prop="created_at" label="时间"></el-table-column>
      </el-table>
    </div>
    
    <div class="points-redeem">
      <h3>积分兑换</h3>
      <div class="reward-list">
        <div class="reward-item" v-for="reward in rewards" :key="reward.id" @click="redeemReward(reward)">
          <div class="reward-icon">{{ reward.icon }}</div>
          <div class="reward-info">
            <h4>{{ reward.name }}</h4>
            <p>{{ reward.description }}</p>
            <div class="reward-price">{{ reward.points }} 碳积分</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CarbonPoints',
  data() {
    return {
      carbonPoints: 120,
      pointsHistory: [
        { id: 1, points: 10, source: '购买图书', created_at: '2026-03-28 10:30:00' },
        { id: 2, points: 10, source: '捐赠图书', created_at: '2026-03-25 14:20:00' },
        { id: 3, points: 20, source: '环保活动', created_at: '2026-03-20 09:15:00' },
        { id: 4, points: 10, source: '购买图书', created_at: '2026-03-15 16:45:00' }
      ],
      rewards: [
        { id: 1, name: '绿植', description: '室内盆栽绿植', points: 50, icon: '🌱' },
        { id: 2, name: '校园优惠券', description: '校园食堂优惠券', points: 30, icon: '🎫' },
        { id: 3, name: '志愿时长', description: '2小时志愿时长', points: 100, icon: '🕒' },
        { id: 4, name: '图书折扣券', description: '图书购买9折券', points: 40, icon: '📚' }
      ]
    }
  },
  methods: {
    redeemReward(reward) {
      if (this.carbonPoints >= reward.points) {
        this.$confirm(`确定要使用 ${reward.points} 碳积分兑换 ${reward.name} 吗？`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.carbonPoints -= reward.points
          this.$message.success('兑换成功')
        }).catch(() => {
          this.$message.info('已取消兑换')
        })
      } else {
        this.$message.error('碳积分不足')
      }
    }
  }
}
</script>

<style scoped>
.carbon-points {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.points-summary {
  margin-bottom: 30px;
}

.points-summary h2 {
  margin-bottom: 20px;
  color: #333;
}

.points-card {
  background: linear-gradient(135deg, #4ecdc4 0%, #45b7d1 100%);
  padding: 40px;
  border-radius: 15px;
  text-align: center;
  color: white;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.points-amount {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.points-label {
  font-size: 1.2rem;
}

.points-history {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.points-history h3 {
  margin-bottom: 20px;
  color: #333;
}

.points-redeem {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.points-redeem h3 {
  margin-bottom: 20px;
  color: #333;
}

.reward-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.reward-item {
  display: flex;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reward-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-color: #4ecdc4;
}

.reward-icon {
  font-size: 2rem;
  margin-right: 20px;
}

.reward-info {
  flex: 1;
}

.reward-info h4 {
  margin-bottom: 5px;
  color: #333;
}

.reward-info p {
  margin-bottom: 10px;
  color: #666;
  font-size: 0.9rem;
}

.reward-price {
  color: #4ecdc4;
  font-weight: bold;
  font-size: 1.1rem;
}
</style>