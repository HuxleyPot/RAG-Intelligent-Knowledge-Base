package com.myrag.backend.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.myrag.backend.common.Result;
import com.myrag.backend.entity.Document;
import com.myrag.backend.mapper.DocumentMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    @Autowired
    private DocumentMapper documentMapper;

    // 上传文件的本地保存目录 (D:/Project/myRAG/data/uploads)
    private static final String UPLOAD_DIR = System.getProperty("user.dir") + "/data/uploads";

    // 1. 上传文档
    @PostMapping("/upload")
    public Result<String> upload(@RequestParam("file") MultipartFile file, @RequestParam("kbId") Long kbId) {
        if (file.isEmpty()) {
            return Result.error("文件为空");
        }

        try {
            // 确保目录存在
            File dir = new File(UPLOAD_DIR);
            if (!dir.exists()) dir.mkdirs();

            // 生成唯一的文件名，防止重名覆盖
            String originalFilename = file.getOriginalFilename();
            String extension = originalFilename.substring(originalFilename.lastIndexOf("."));
            String newFileName = UUID.randomUUID().toString() + extension;
            File destFile = new File(UPLOAD_DIR + "/" + newFileName);

            // 保存文件到本地磁盘
            file.transferTo(destFile);

            // 保存记录到数据库
            Document doc = new Document();
            doc.setKbId(kbId);
            doc.setFilename(originalFilename);
            doc.setFilePath(destFile.getAbsolutePath());
            doc.setStatus("PROCESSING"); // 初始状态为处理中
            doc.setCreatedAt(LocalDateTime.now());
            documentMapper.insert(doc);

            return Result.success("上传成功");

        } catch (IOException e) {
            e.printStackTrace();
            return Result.error("文件保存失败: " + e.getMessage());
        }
    }

    // 2. 获取某知识库下的文档列表
    @GetMapping("/list/{kbId}")
    public Result<List<Document>> list(@PathVariable Long kbId) {
        List<Document> list = documentMapper.selectList(
                new LambdaQueryWrapper<Document>()
                        .eq(Document::getKbId, kbId)
                        .orderByDesc(Document::getCreatedAt)
        );
        return Result.success(list);
    }
}