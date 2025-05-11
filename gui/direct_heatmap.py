def update_region_heatmap_view(self, region_data, max_value):
    """显示地域分布热力图视图"""
    try:
        import json
        print("渲染热力图视图...")
        
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
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/map/js/china.js"></script>
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
            
            // 页面加载完成后初始化
            window.addEventListener('load', function() {{
                try {{
                    log("页面加载完成，开始初始化...");
                    
                    if (typeof echarts === 'undefined') {{
                        log("ECharts未加载，切换到表格视图", true);
                        showFallback();
                        return;
                    }}
                    
                    log("ECharts已成功加载，开始渲染地图...");
                    
                    // 初始化ECharts实例
                    var chart = echarts.init(document.getElementById('main'));
                    
                    // 准备数据
                    var mapData = {map_data_json};
                    var maxValue = {max_value};
                    
                    // 检查数据
                    log("地图数据准备完成: " + mapData.length + " 条数据");
                    
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
                            formatter: function(params) {{
                                return params.name + '<br/>搜索指数: ' + (params.value || 0);
                            }}
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
                                    min: 0.5,
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
                    log("渲染地图出错: " + e.message, true);
                    showFallback();
                }}
            }});
            
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
        import logging
        logging.error(f"更新地域分布热力图时出错: {{str(e)}}")
        print(f"错误: {{str(e)}}")
        import traceback
        traceback.print_exc()
        
        # 如果出现错误，尝试切换到表格视图
        try:
            if hasattr(self, 'region_view_selector'):
                self.region_view_selector.setCurrentIndex(0)  # 切换到表格视图
        except:
            pass


def handle_url_changed(self, url):
    """处理URL变化，检测是否需要切换到表格视图"""
    try:
        url_string = url.toString()
        if "fallback=true" in url_string:
            print("检测到热力图请求回退到表格视图")
            if hasattr(self, 'region_view_selector'):
                # 临时断开信号连接，避免循环
                self.region_view_selector.blockSignals(True)
                self.region_view_selector.setCurrentIndex(0)  # 切换到表格视图
                self.region_view_selector.blockSignals(False)
    except Exception as e:
        print(f"处理URL变化时出错: {{str(e)}}")
