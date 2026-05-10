        // 加载晋级竞猜页面
        function loadKnockoutPage() {
            if (!currentUser) {
                document.getElementById('knockout-login-area').innerHTML = `
                    <div class="input-group">
                        <label>你的姓名</label>
                        <input type="text" id="knockout-user-input" placeholder="请输入你的姓名">
                    </div>
                    <button class="btn btn-block" onclick="saveKnockoutUser()">确认姓名</button>
                `;
                document.getElementById('knockout-area').style.display = 'none';
                document.getElementById('knockout-login-area').style.display = 'block';
                return;
            }
            
            // 检查是否锁定
            fetch('/api/knockout/load?user=' + encodeURIComponent(currentUser))
            .then(res => res.json())
            .then(data => {
                if (data.locked) {
                    document.getElementById('knockout-area').innerHTML = `
                        <div class="alert alert-warning">
                            ⚠️ 晋级竞猜已锁定（第一场比赛前1小时）！
                        </div>
                    `;
                    document.getElementById('knockout-area').style.display = 'block';
                    return;
                }
                
                document.getElementById('knockout-login-area').style.display = 'none';
                document.getElementById('knockout-area').style.display = 'block';
                document.getElementById('knockout-user-name').textContent = currentUser;
                
                // 加载已有预测
                const predictions = data.predictions || {};
                
                // 渲染各轮次输入框
                renderKnockoutInput('knockout-32', 32, '32强', predictions['32强'] || []);
                renderKnockoutInput('knockout-16', 16, '16强', predictions['16强'] || []);
                renderKnockoutInput('knockout-8', 8, '8强', predictions['8强'] || []);
                renderKnockoutInput('knockout-4', 4, '4强', predictions['4强'] || []);
                renderKnockoutInput('knockout-2', 2, '2强', predictions['2强'] || []);
                renderKnockoutInput('knockout-1', 1, '冠军', predictions['冠军'] || []);
            });
        }
        
        // 渲染晋级竞猜输入框
        function renderKnockoutInput(containerId, maxTeams, roundName, existingPredictions) {
            const container = document.getElementById(containerId);
            container.innerHTML = '';
            
            for (let i = 0; i < maxTeams; i++) {
                const input = document.createElement('input');
                input.type = 'text';
                input.placeholder = `队伍${i+1}名称`;
                input.value = existingPredictions[i] || '';
                input.id = `knockout-${roundName}-${i}`;
                input.style.cssText = 'width:100%;padding:8px;margin-bottom:5px;border:2px solid #ddd;border-radius:8px;';
                container.appendChild(input);
            }
        }
        
        // 保存晋级竞猜
        function saveKnockoutPredictions() {
            if (!currentUser) {
                alert('请先输入姓名！');
                return;
            }
            
            const predictions = {};
            predictions['32强'] = getKnockoutInputs('32强', 32);
            predictions['16强'] = getKnockoutInputs('16强', 16);
            predictions['8强'] = getKnockoutInputs('8强', 8);
            predictions['4强'] = getKnockoutInputs('4强', 4);
            predictions['2强'] = getKnockoutInputs('2强', 2);
            predictions['冠军'] = getKnockoutInputs('冠军', 1);
            
            fetch('/api/knockout/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user: currentUser,
                    predictions: predictions
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert('✅ 晋级竞猜已保存！');
                } else {
                    alert('❌ ' + data.message);
                }
            });
        }
        
        // 获取晋级竞猜输入框的值
        function getKnockoutInputs(roundName, maxTeams) {
            const results = [];
            for (let i = 0; i < maxTeams; i++) {
                const input = document.getElementById(`knockout-${roundName}-${i}`);
                if (input && input.value.trim()) {
                    results.push(input.value.trim());
                }
            }
            return results;
        }
        
        // 保存晋级竞猜的用户名
        function saveKnockoutUser() {
            const name = document.getElementById('knockout-user-input').value.trim();
            if (!name) {
                alert('请输入姓名！');
                return;
            }
            currentUser = name;
            fetch('/api/set_user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user: name})
            })
            .then(() => loadKnockoutPage());
        }
