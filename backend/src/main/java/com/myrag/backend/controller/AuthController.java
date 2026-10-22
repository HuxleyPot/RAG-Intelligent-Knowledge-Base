package com.myrag.backend.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.myrag.backend.common.JwtUtil;
import com.myrag.backend.common.Result;
import com.myrag.backend.entity.LoginDTO;
import com.myrag.backend.entity.User;
import com.myrag.backend.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private UserMapper userMapper;

    @Autowired
    private JwtUtil jwtUtil;

    // 密码加密器
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @PostMapping("/login")
    public Result<Map<String, String>> login(@RequestBody LoginDTO dto) {
        // 1. 查数据库找用户
        User user = userMapper.selectOne(new LambdaQueryWrapper<User>()
                .eq(User::getUsername, dto.getUsername()));

        // 2. 校验用户是否存在（这里我们先用明文比对测试，稍后你可以改成BCrypt）
        // 注意：咱们之前数据库插的是 '123456' 明文
        if (user == null || !dto.getPassword().equals(user.getPasswordHash())) {
            return Result.error("用户名或密码错误");
        }

        // 3. 生成 Token
        String token = jwtUtil.generateToken(user.getId(), user.getUsername());

        // 4. 返回给前端
        Map<String, String> data = new HashMap<>();
        data.put("token", token);
        data.put("username", user.getUsername());
        
        return Result.success(data);
    }
}