"""
热力图修复补丁 - 兼容版本

此文件包含解决热力图显示问题的函数，特别修复了setLinkDelegationPolicy不兼容的问题。
"""

def update_region_heatmap_view(self, region_data, max_value):
    """显示地域分布热力图视图"""
    try:
        import json
        import os
        from PyQt5.QtCore import QUrl, QTimer
        
        print("渲染热力图视图...")
        
        # 确定资源文件路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resources_dir = os.path.join(base_dir, "resources")
        
        # 获取文件路径
        echarts_js_path = os.path.join(resources_dir, "echarts.js")
        echarts_min_js_path = os.path.join(resources_dir, "echarts.min.js")
        china_js_path = os.path.join(resources_dir, "china.js")
        
        # 检查文件存在，优先使用echarts.js
        echarts_exists = os.path.exists(echarts_js_path)
        echarts_min_exists = os.path.exists(echarts_min_js_path)
        china_exists = os.path.exists(china_js_path)
        
        # 选择要使用的文件路径
        if echarts_exists:
            echarts_path = echarts_js_path
            print(f"将使用完整版echarts.js: {echarts_path}")
        elif echarts_min_exists:
            echarts_path = echarts_min_js_path
            print(f"将使用压缩版echarts.min.js: {echarts_path}")
        else:
            print("本地未找到ECharts库文件，将尝试从CDN加载")
            echarts_path = None
        
        # 获取文件URLs
        if echarts_path:
            # 将路径转换为文件URL
            # Windows下需要确保路径格式正确
            echarts_path = echarts_path.replace('\\', '/')
            if not echarts_path.startswith('/'):
                echarts_path = '/' + echarts_path
            
            # 生成本地文件URL
            echarts_url = f"file://{echarts_path}"
            print(f"ECharts URL: {echarts_url}")
        else:
            echarts_url = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"
            print(f"使用CDN地址: {echarts_url}")
        
        # 转换为JSON字符串，用于ECharts
        map_data_json = json.dumps(region_data)
        
        # 创建直接内嵌ECharts代码和地图数据的HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>地域分布热力图</title>
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    background-color: #1a237e;
                    color: white;
                    font-family: Arial, sans-serif;
                    width: 100%;
                    height: 100%;
                    overflow: hidden;
                }}
                #main {{
                    width: 100%;
                    height: 600px;
                }}
                #error-log {{
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    color: #ff5722;
                    background-color: rgba(0,0,0,0.5);
                    padding: 5px;
                    font-size: 12px;
                    height: 100px;
                    overflow: auto;
                    display: block;
                }}
                .error {{
                    color: #ff5722;
                }}
                .success {{
                    color: #4caf50;
                }}
                .fallback {{
                    text-align: center;
                    padding-top: 100px;
                }}
            </style>
        </head>
        <body>
            <div id="main"></div>
            <div id="error-log"></div>
            
            <script>
            // 调试函数
            function log(message, isError) {{
                var logElement = document.getElementById('error-log');
                var p = document.createElement('p');
                p.className = isError ? 'error' : 'success';
                p.textContent = message;
                logElement.appendChild(p);
                console.log(message);
            }}
            
            // 加载echarts.js
            log("页面加载完成，开始初始化...");
            
            // 加载ECharts库
            var echartsLoaded = false;
            
            function loadECharts() {{
                // 创建script标签加载ECharts
                var script = document.createElement('script');
                script.onload = function() {{
                    log("ECharts加载成功");
                    echartsLoaded = true;
                    initChart();
                }};
                script.onerror = function() {{
                    log("ECharts本地加载失败，尝试CDN", true);
                    loadEChartsFromCDN();
                }};
                script.src = "{echarts_url}";
                document.head.appendChild(script);
            }}
            
            function loadEChartsFromCDN() {{
                // 从CDN加载ECharts
                var script = document.createElement('script');
                script.onload = function() {{
                    log("ECharts从CDN加载成功");
                    echartsLoaded = true;
                    initChart();
                }};
                script.onerror = function() {{
                    log("ECharts从CDN加载失败，无法加载热力图", true);
                    showFallback();
                }};
                script.src = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js";
                document.head.appendChild(script);
            }}
            
            function initChart() {{
                if (typeof echarts === 'undefined') {{
                    log("ECharts未定义，加载失败", true);
                    showFallback();
                    return;
                }}
                
                // 注册地图
                registerMap();
            }}
            
            function registerMap() {{
                try {{
                    // 简化版地图数据（无需外部地图文件）
                    var chinaJson = {{
                        "type": "FeatureCollection",
                        "features": [
                            {{ "type": "Feature", "properties": {{ "name": "北京" }}, "id": "110000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "天津" }}, "id": "120000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "河北" }}, "id": "130000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "山西" }}, "id": "140000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "内蒙古" }}, "id": "150000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "辽宁" }}, "id": "210000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "吉林" }}, "id": "220000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "黑龙江" }}, "id": "230000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "上海" }}, "id": "310000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "江苏" }}, "id": "320000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "浙江" }}, "id": "330000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "安徽" }}, "id": "340000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "福建" }}, "id": "350000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "江西" }}, "id": "360000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "山东" }}, "id": "370000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "河南" }}, "id": "410000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "湖北" }}, "id": "420000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "湖南" }}, "id": "430000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "广东" }}, "id": "440000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "广西" }}, "id": "450000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "海南" }}, "id": "460000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "重庆" }}, "id": "500000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "四川" }}, "id": "510000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "贵州" }}, "id": "520000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "云南" }}, "id": "530000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "西藏" }}, "id": "540000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "陕西" }}, "id": "610000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "甘肃" }}, "id": "620000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "青海" }}, "id": "630000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "宁夏" }}, "id": "640000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "新疆" }}, "id": "650000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "台湾" }}, "id": "710000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "香港" }}, "id": "810000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }},
                            {{ "type": "Feature", "properties": {{ "name": "澳门" }}, "id": "820000", "geometry": {{ "type": "Polygon", "coordinates": [[]] }} }}
                        ]
                    }};
                    
                    // 注册地图
                    echarts.registerMap('china', chinaJson);
                    log("成功注册中国地图");
                    
                    // 渲染图表
                    renderChart();
                }} catch (e) {{
                    log("注册地图失败: " + e.message, true);
                    showFallback();
                }}
            }}
            
            function renderChart() {{
                try {{
                    // 初始化ECharts实例
                    var chart = echarts.init(document.getElementById('main'));
                    log("ECharts实例初始化成功");
                    
                    // 准备数据
                    var mapData = {map_data_json};
                    var maxValue = {max_value};
                    
                    // 配置选项
                    var option = {{
                        title: {{
                            text: '地域分布热力图',
                            subtext: '基于百度指数的地域分布数据',
                            left: 'center',
                            textStyle: {{
                                color: '#ffffff'
                            }},
                            subtextStyle: {{
                                color: '#cccccc'
                            }}
                        }},
                        tooltip: {{
                            trigger: 'item',
                            formatter: '{{b}}<br/>搜索指数: {{c}}'
                        }},
                        toolbox: {{
                            show: true,
                            orient: 'vertical',
                            left: 'right',
                            top: 'center',
                            feature: {{
                                dataView: {{readOnly: false}},
                                restore: {{}},
                                saveAsImage: {{}}
                            }},
                            iconStyle: {{
                                color: '#ffffff'
                            }}
                        }},
                        visualMap: {{
                            min: 0,
                            max: maxValue,
                            left: '10%',
                            top: 'middle',
                            text: ['高', '低'],
                            calculable: true,
                            inRange: {{
                                color: ['#C6E2FF', '#1E90FF', '#002366']
                            }},
                            textStyle: {{
                                color: '#fff'
                            }}
                        }},
                        series: [
                            {{
                                name: '搜索指数',
                                type: 'map',
                                map: 'china',
                                roam: true,
                                zoom: 1.2,
                                scaleLimit: {{
                                    min: 1,
                                    max: 3
                                }},
                                itemStyle: {{
                                    areaColor: '#323c48',
                                    borderColor: '#111'
                                }},
                                emphasis: {{
                                    itemStyle: {{
                                        areaColor: '#ff5722'
                                    }},
                                    label: {{
                                        show: true,
                                        color: '#fff'
                                    }}
                                }},
                                data: mapData
                            }}
                        ]
                    }};
                    
                    // 应用配置
                    chart.setOption(option);
                    log("地图渲染完成");
                    
                    // 窗口大小改变时重新调整大小
                    window.addEventListener('resize', function() {{
                        chart.resize();
                    }});
                    
                    // 10秒后隐藏日志
                    setTimeout(function() {{
                        var logElement = document.getElementById('error-log');
                        logElement.style.height = '20px';
                        logElement.style.opacity = '0.5';
                    }}, 10000);
                }} catch (e) {{
                    log("渲染图表失败: " + e.message, true);
                    showFallback();
                }}
            }}
            
            function showFallback() {{
                log("显示备用表格视图", false);
                document.getElementById('main').innerHTML = `
                <div class="fallback">
                    <h2>热力图加载失败</h2>
                    <p>正在为您显示备用表格数据...</p>
                </div>
                `;
                
                // 通知PyQt跳转到表格视图
                setTimeout(function() {{
                    window.location.href = 'about:blank?fallback=true';
                }}, 2000);
            }}
            
            // 开始加载ECharts
            loadECharts();
            </script>
        </body>
        </html>
        """

        # 更新地图显示
        self.region_map_view.setHtml(html)
        print("热力图HTML已更新")
        
        # 监听URL变化事件，如果包含fallback参数，切换到表格视图
        self.region_map_view.urlChanged.connect(self.handle_url_changed)
        
    except Exception as e:
        logging.error(f"更新地域分布热力图时出错: {str(e)}")
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 如果出现错误，尝试切换到表格视图
        try:
            if hasattr(self, 'region_view_selector'):
                self.region_view_selector.setCurrentIndex(0)  # 切换到表格视图
        except:
            pass 