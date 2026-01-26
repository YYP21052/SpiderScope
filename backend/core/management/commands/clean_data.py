"""
@Time ： 2026/1/22
@Auth ： CST21052
@File ：clean_data.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:爬虫数据清洗
"""
import re
from django.core.management.base import BaseCommand
from core.models import Job


class Command(BaseCommand):
    help = '清洗职位数据：格式化薪资，去重标签'

    def handle(self, *args, **options):
        self.stdout.write("🧹 开始清洗数据...")

        jobs = Job.objects.all()
        count = 0

        for job in jobs:
            # 1. 清洗薪资 (核心逻辑)
            # 目标：把 "1.5-2.5万" -> 15000, 25000
            raw_salary = job.salary
            min_val, max_val = 0, 0

            if raw_salary:
                # 统一单位：如果是 "万/月" 或 "万"，数值 * 10000
                # 如果是 "千/月"，数值 * 1000
                # 如果是 "元/天" (实习)，数值 * 22 (按22天算月薪)

                # 提取数字 (支持小数，如 1.5)
                nums = re.findall(r'(\d+\.?\d*)', raw_salary)

                if nums:
                    # 转换基础数字
                    v1 = float(nums[0])
                    v2 = float(nums[1]) if len(nums) > 1 else v1

                    # 判断单位
                    if '万' in raw_salary:
                        min_val = int(v1 * 10000)
                        max_val = int(v2 * 10000)
                    elif '千' in raw_salary:
                        min_val = int(v1 * 1000)
                        max_val = int(v2 * 1000)
                    elif '天' in raw_salary:  # 实习生，例如 150/天
                        min_val = int(v1 * 22)  # 估算月薪
                        max_val = int(v2 * 22)
                    else:
                        # 既没万也没千，假设是元年薪 (极少情况) 或者已经清洗过
                        pass

            # 2. 写入数据库
            job.min_salary = min_val
            job.max_salary = max_val

            # 3. 简单的 Tags 清洗 (去重 + 去掉空值)
            if job.tags:
                tag_list = job.tags.replace('，', ',').split(',')
                clean_tags = [t.strip() for t in tag_list if t.strip()]
                # 去重
                clean_tags = list(set(clean_tags))
                job.tags = ",".join(clean_tags)

            job.save()
            count += 1
            if count % 50 == 0:
                self.stdout.write(f"   ⏳ 已处理 {count} 条...")

        self.stdout.write(self.style.SUCCESS(f"✅ 清洗完成！共处理 {count} 条职位数据。"))