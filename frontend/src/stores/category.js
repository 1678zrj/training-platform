import {defineStore} from "pinia";
import {ref} from "vue";
import axios from "axios";
import {ElMessage} from "element-plus";

export const useCategoryStore = defineStore('category',() =>{
  const categories = ref([])
  const fetchCategories = async () =>{
    try {
      const res = await axios.get('/api/v1/categories/')
      categories.value = res.data
    }catch (error){
      console.error('获取实验分类失败',error)
      ElMessage.error('无法加载教学资源分类目录')
    }

  }
  return {categories, fetchCategories}
})