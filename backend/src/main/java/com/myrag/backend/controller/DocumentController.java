package com.myrag.backend.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.myrag.backend.common.Result;
import com.myrag.backend.entity.Document;
import com.myrag.backend.mapper.DocumentMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.client.RestTemplate;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

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

    private final RestTemplate restTemplate = new RestTemplate();
    private static final String UPLOAD_DIR = System.getProperty("user.dir") + "/data/uploads";

    @PostMapping("/upload")
    public Result<String> upload(@RequestParam("file") MultipartFile file, @RequestParam("kbId") Long kbId) {
        if (file.isEmpty()) return Result.error("文件为空");

        try {
            File dir = new File(UPLOAD_DIR);
            if (!dir.exists()) dir.mkdirs();

            String originalFilename = file.getOriginalFilename();
            String extension = originalFilename.substring(originalFilename.lastIndexOf("."));
            String newFileName = UUID.randomUUID().toString() + extension;
            File destFile = new File(UPLOAD_DIR + "/" + newFileName);

            file.transferTo(destFile);

            Document doc = new Document();
            doc.setKbId(kbId);
            doc.setFilename(originalFilename);
            doc.setFilePath(destFile.getAbsolutePath());
            doc.setStatus("PROCESSING");
            doc.setCreatedAt(LocalDateTime.now());
            documentMapper.insert(doc);

            try {
                MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
                body.add("file_path", destFile.getAbsolutePath());
                body.add("kb_id", kbId);
                body.add("doc_id", doc.getId());
                restTemplate.postForEntity("http://localhost:18000/api/v1/documents/process", body, String.class);
            } catch (Exception e) {
                System.err.println("调用 Python 服务失败: " + e.getMessage());
            }
            return Result.success("上传成功");
        } catch (IOException e) {
            return Result.error("文件保存失败: " + e.getMessage());
        }
    }

    @GetMapping("/list/{kbId}")
    public Result<List<Document>> list(@PathVariable Long kbId) {
        List<Document> list = documentMapper.selectList(
                new LambdaQueryWrapper<Document>().eq(Document::getKbId, kbId).orderByDesc(Document::getCreatedAt)
        );
        return Result.success(list);
    }

    // 👇 新增：接收 Python 回调，更新状态
    @PostMapping("/{id}/status")
    public Result<String> updateStatus(@PathVariable Long id, @RequestParam String status) {
        Document doc = documentMapper.selectById(id);
        if (doc != null) {
            doc.setStatus(status);
            documentMapper.updateById(doc);
            System.out.println("============== 文档状态已更新: " + id + " -> " + status + " ==============");
            return Result.success("状态更新成功");
        }
        return Result.error("文档不存在");
    }

        // 新增：转发前端问答请求到 Python AI 服务
    @PostMapping("/chat")
    public Result<Object> chat(@RequestParam String question, @RequestParam Long kbId) {
        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("question", question);
            body.add("kb_id", kbId);

            // 请求 Python 的 RAG 接口
            String pythonUrl = "http://localhost:18000/api/v1/rag/answer";
            Object response = restTemplate.postForObject(pythonUrl, body, Object.class);
            
            // 因为 Python 返回的本身就是 {code, message, data}，所以直接透传
            return Result.success(response);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error("问答请求失败: " + e.getMessage());
        }
    }


}