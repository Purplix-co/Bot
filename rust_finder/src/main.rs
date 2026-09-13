use std::env;
use std::fs;
use std::path::Path;
use walkdir::WalkDir;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("❌ Укажи имя программы");
        process::exit(1);
    }

    let name = &args[1].to_lowercase();
    let memory_path = if args.len() > 2 {
        args[2].clone()
    } else {
        "./data/assistant_data.json".to_string()
    };

    // Проверяем память
    if let Ok(content) = fs::read_to_string(&memory_path) {
        if let Ok(json) = serde_json::from_str::<serde_json::Value>(&content) {
            if let Some(programs) = json.get("programs") {
                if let Some(path) = programs.get(name) {
                    if let Some(path_str) = path.as_str() {
                        if Path::new(path_str).exists() {
                            println!("{}", path_str);
                            return;
                        }
                    }
                }
            }
        }
    }

    // === Файлы, которые нужно игнорировать ===
    let bad_patterns = vec![
        "crashhandler",
        "launcher",
        "updater",
        "helper",
        "installer",
        "setup",
        "uninstall",
        "patcher",
        "service",
        "background",
        "crashes",
        "betas",
    ];

    let username = env::var("USERNAME").unwrap_or_default();

    let dirs = vec![
        format!("C:/Program Files"),
        format!("C:/Program Files (x86)"),
        format!("C:/Users/{}/AppData/Local", username),
        format!("C:/Users/{}/AppData/Roaming", username),
        format!("C:/Users/{}/AppData/Local/Programs", username),
        format!("C:/Users/{}/Desktop", username),
        format!("C:/Users/{}/Downloads", username),
        "C:/ProgramData".to_string(),
        "C:/Windows".to_string(),
        "C:/Windows/System32".to_string(),
    ];

    // Сначала ищем .exe, потом .lnk
    let extensions_priority = vec![
        vec!["exe"],
        vec!["lnk"],
        vec!["bat", "cmd", "com", "msi", "ps1", "jar"],
    ];

    for ext_group in extensions_priority {
        for dir in &dirs {
            if !Path::new(dir).exists() {
                continue;
            }

            if let Ok(entries) = fs::read_dir(dir) {
                for entry in entries.flatten() {
                    let path = entry.path();

                    if path.is_file() {
                        if let Some(ext) = path.extension() {
                            let ext_str = ext.to_string_lossy().to_lowercase();
                            if ext_group.contains(&ext_str.as_str()) {
                                if let Some(stem) = path.file_stem() {
                                    let stem_lower = stem.to_string_lossy().to_lowercase();
                                    if stem_lower.contains(name) {
                                        // === ПРОВЕРКА НА МУСОРНЫЕ ФАЙЛЫ ===
                                        let mut is_bad = false;
                                        for pattern in &bad_patterns {
                                            if stem_lower.contains(pattern) {
                                                is_bad = true;
                                                break;
                                            }
                                        }
                                        if !is_bad {
                                            println!("{}", path.display());
                                            return;
                                        }
                                    }
                                }
                            }
                        }
                    }

                    if path.is_dir() {
                        for result in WalkDir::new(path).max_depth(4).into_iter().flatten() {
                            let p = result.path();
                            if p.is_file() {
                                if let Some(ext) = p.extension() {
                                    let ext_str = ext.to_string_lossy().to_lowercase();
                                    if ext_group.contains(&ext_str.as_str()) {
                                        if let Some(stem) = p.file_stem() {
                                            let stem_lower = stem.to_string_lossy().to_lowercase();
                                            if stem_lower.contains(name) {
                                                let mut is_bad = false;
                                                for pattern in &bad_patterns {
                                                    if stem_lower.contains(pattern) {
                                                        is_bad = true;
                                                        break;
                                                    }
                                                }
                                                if !is_bad {
                                                    println!("{}", p.display());
                                                    return;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    process::exit(1);
}