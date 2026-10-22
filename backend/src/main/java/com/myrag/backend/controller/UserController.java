package com.myrag.backend.controller;

import com.myrag.backend.common.Result; // 引入刚才写的类
import com.myrag.backend.entity.User;
import com.myrag.backend.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserMapper userMapper;

    @GetMapping
    public Result<List<User>> listAll() {
        List<User> list = userMapper.selectList(null);
        return Result.success(list); // 套上统一的外壳返回
    }
}