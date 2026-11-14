/* Interaksi antarmuka FEAF (v1.1) — JavaScript murni tanpa pustaka luar.
   Semua halaman tetap berfungsi penuh apabila JavaScript dimatikan. */
(function () {
  "use strict";

  /* 1. Laci navigasi ponsel (< 900px) */
  var rail = document.querySelector(".rail");
  var latar = document.querySelector(".latar-laci");
  function aturLaci(buka) {
    if (!rail) return;
    rail.classList.toggle("buka", buka);
    if (latar) latar.classList.toggle("buka", buka);
    document.body.classList.toggle("laci-terbuka", buka);
  }
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-buka-menu]")) {
      e.preventDefault();
      aturLaci(!rail || !rail.classList.contains("buka"));
    } else if (e.target.closest("[data-tutup-menu]") || e.target === latar) {
      aturLaci(false);
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      aturLaci(false);
      document.querySelectorAll(".info.buka").forEach(function (el) {
        el.classList.remove("buka");
      });
    }
  });

  /* 2. Tombol tutup pita pemberitahuan */
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-tutup-pita]");
    if (!t) return;
    var pita = t.closest(".pita");
    if (pita) pita.remove();
  });

  /* 3. Tooltip ⓘ ramah sentuh di ponsel */
  document.addEventListener("click", function (e) {
    var info = e.target.closest(".info");
    document.querySelectorAll(".info.buka").forEach(function (el) {
      if (el !== info) el.classList.remove("buka");
    });
    if (info) {
      e.preventDefault();
      e.stopPropagation();
      info.classList.toggle("buka");
    }
  });

  /* 4. Filter sisi klien di Feed Peringatan (status + jenis + sembunyikan arsip bawaan) */
  var barisFeed = Array.prototype.slice.call(document.querySelectorAll(".baris[data-status]"));
  if (barisFeed.length > 0) {
    var params = new URLSearchParams(window.location.search);
    var stAktif = params.get("status") || "semua";
    var jnAktif = params.get("jenis") || "semua";
    var tampilArsip = params.get("arsip") === "1" || stAktif === "dilewati";

    function terapkanFilterFeed() {
      var tampil = 0;
      barisFeed.forEach(function (b) {
        var stBaris = b.getAttribute("data-status");
        var cocokSt;
        if (stAktif === "semua") {
          cocokSt = stBaris !== "dilewati" || tampilArsip;
        } else {
          cocokSt = stBaris === stAktif;
        }
        var cocokJn = jnAktif === "semua" || b.getAttribute("data-jenis-grup") === jnAktif;
        var ok = cocokSt && cocokJn;
        b.hidden = !ok;
        if (ok) tampil += 1;
      });
      document.querySelectorAll(".kelompok-tanggal").forEach(function (g) {
        var ada = g.querySelectorAll(".baris[data-status]:not([hidden])").length > 0;
        g.hidden = !ada;
      });
      document.querySelectorAll("[data-filter-status]").forEach(function (el) {
        var on = el.getAttribute("data-filter-status") === stAktif;
        el.classList.toggle("on", on);
        el.setAttribute("aria-pressed", on ? "true" : "false");
      });
      document.querySelectorAll("[data-filter-jenis]").forEach(function (el) {
        var on = el.getAttribute("data-filter-jenis") === jnAktif;
        el.classList.toggle("on", on);
        el.setAttribute("aria-pressed", on ? "true" : "false");
      });
      document.querySelectorAll("[data-tampil-arsip]").forEach(function (el) {
        var aktifArsip = tampilArsip || stAktif === "dilewati";
        el.classList.toggle("on", aktifArsip);
        el.setAttribute("aria-pressed", aktifArsip ? "true" : "false");
      });
      var kosongFilter = document.getElementById("feed-kosong-filter");
      if (kosongFilter) kosongFilter.hidden = tampil > 0;

      var u = new URL(window.location.href);
      if (stAktif && stAktif !== "semua") u.searchParams.set("status", stAktif);
      else u.searchParams.delete("status");
      if (jnAktif && jnAktif !== "semua") u.searchParams.set("jenis", jnAktif);
      else u.searchParams.delete("jenis");
      if (tampilArsip && stAktif === "semua") u.searchParams.set("arsip", "1");
      else u.searchParams.delete("arsip");
      if (window.history && window.history.replaceState) {
        window.history.replaceState(null, "", u.pathname + u.search);
      }
    }

    document.addEventListener("click", function (e) {
      var kArsip = e.target.closest("[data-tampil-arsip]");
      if (kArsip) {
        e.preventDefault();
        if (stAktif === "dilewati") {
          stAktif = "semua";
          tampilArsip = false;
        } else {
          tampilArsip = !tampilArsip;
        }
        terapkanFilterFeed();
        return;
      }
      var kSt = e.target.closest("[data-filter-status]");
      if (kSt) {
        e.preventDefault();
        var pilihSt = kSt.getAttribute("data-filter-status");
        stAktif = stAktif === pilihSt && pilihSt !== "semua" ? "semua" : pilihSt;
        terapkanFilterFeed();
        return;
      }
      var kJn = e.target.closest("[data-filter-jenis]");
      if (kJn) {
        e.preventDefault();
        var pilihJn = kJn.getAttribute("data-filter-jenis");
        jnAktif = jnAktif === pilihJn && pilihJn !== "semua" ? "semua" : pilihJn;
        terapkanFilterFeed();
      }
    });

    terapkanFilterFeed();
  }

  /* 5. Filter sisi klien di halaman Review (jenis sebab) */
  var kartuReview = Array.prototype.slice.call(document.querySelectorAll("[data-sebab-review]"));
  if (kartuReview.length > 0) {
    var sebabAktif = "semua";
    document.addEventListener("click", function (e) {
      var chip = e.target.closest("[data-filter-sebab]");
      if (!chip) return;
      e.preventDefault();
      var pilih = chip.getAttribute("data-filter-sebab");
      sebabAktif = sebabAktif === pilih && pilih !== "semua" ? "semua" : pilih;
      kartuReview.forEach(function (k) {
        k.hidden = !(sebabAktif === "semua" || k.getAttribute("data-sebab-review") === sebabAktif);
      });
      document.querySelectorAll("[data-filter-sebab]").forEach(function (c) {
        var on = c.getAttribute("data-filter-sebab") === sebabAktif;
        c.classList.toggle("on", on);
        c.setAttribute("aria-pressed", on ? "true" : "false");
      });
    });
  }

  /* 6. Saran otomatis pencarian emiten (Watchlist & kotak cari) */
  document.querySelectorAll("[data-cari-saran]").forEach(function (input) {
    var bungkus = input.closest(".bungkus-saran") || input.parentElement;
    bungkus.style.position = "relative";
    var kotak = document.createElement("div");
    kotak.className = "daftar-saran";
    kotak.hidden = true;
    bungkus.appendChild(kotak);
    var timer = null;
    var hasilTerakhir = [];

    function tutupSaran() {
      kotak.hidden = true;
      kotak.innerHTML = "";
    }

    input.addEventListener("input", function () {
      var q = input.value.trim();
      clearTimeout(timer);
      if (q.length < 1) {
        hasilTerakhir = [];
        tutupSaran();
        return;
      }
      timer = setTimeout(function () {
        fetch("/api/search?q=" + encodeURIComponent(q))
          .then(function (r) { return r.ok ? r.json() : []; })
          .then(function (daftar) {
            hasilTerakhir = Array.isArray(daftar) ? daftar : [];
            if (!hasilTerakhir.length) {
              tutupSaran();
              return;
            }
            kotak.innerHTML = "";
            hasilTerakhir.slice(0, 8).forEach(function (it) {
              var btn = document.createElement("button");
              btn.type = "button";
              btn.className = "item-saran";
              var kd = document.createElement("span");
              kd.className = "mono kd";
              kd.textContent = it.kode;
              var nm = document.createElement("span");
              nm.className = "nm";
              nm.textContent = (it.nama || "") + (it.nama_en ? " · " + it.nama_en : "");
              var br = document.createElement("span");
              br.className = "bursa mono";
              br.textContent = it.bursa || "";
              btn.appendChild(kd);
              btn.appendChild(nm);
              btn.appendChild(br);
              btn.addEventListener("click", function () {
                input.value = it.kode;
                tutupSaran();
                input.focus();
              });
              kotak.appendChild(btn);
            });
            kotak.hidden = false;
          })
          .catch(function () { tutupSaran(); });
      }, 140);
    });

    var form = input.closest("form");
    if (form && input.getAttribute("data-cari-saran") === "kode") {
      form.addEventListener("submit", function (e) {
        var v = input.value.trim();
        if (!v || /^\d{4,6}$/.test(v)) return;
        if (hasilTerakhir.length > 0 && hasilTerakhir[0].kode) {
          input.value = hasilTerakhir[0].kode;
          return;
        }
        e.preventDefault();
        fetch("/api/search?q=" + encodeURIComponent(v))
          .then(function (r) { return r.ok ? r.json() : []; })
          .then(function (d) {
            if (Array.isArray(d) && d.length > 0 && d[0].kode) {
              input.value = d[0].kode;
            }
            HTMLFormElement.prototype.submit.call(form);
          })
          .catch(function () {
            HTMLFormElement.prototype.submit.call(form);
          });
      });
    }

    document.addEventListener("click", function (e) {
      if (!bungkus.contains(e.target)) tutupSaran();
    });
  });

  /* 7. Konfirmasi sebelum menghapus item dari watchlist */
  document.addEventListener("submit", function (e) {
    var form = e.target.closest("form[data-konfirmasi]");
    if (!form) return;
    var pesan = form.getAttribute("data-konfirmasi");
    if (pesan && !window.confirm(pesan)) {
      e.preventDefault();
    }
  });

  /* 8. Status loading pada form aksi dan tautan segarkan (A1.2a) */
  function tandaiMemuat(btn) {
    if (!btn) return;
    btn.classList.add("sedang-memuat");
    btn.setAttribute("aria-busy", "true");
    if (btn.tagName === "A") {
      btn.setAttribute("aria-disabled", "true");
    }
  }

  function bersihkanMemuat() {
    document.querySelectorAll("form[data-sedang-kirim]").forEach(function (f) {
      delete f.dataset.sedangKirim;
    });
    document.querySelectorAll(".sedang-memuat").forEach(function (el) {
      el.classList.remove("sedang-memuat");
      el.removeAttribute("aria-busy");
      el.removeAttribute("aria-disabled");
      if ("disabled" in el) el.disabled = false;
    });
    document.querySelectorAll("button[data-dinonaktifkan-kirim]").forEach(function (b) {
      delete b.dataset.dinonaktifkanKirim;
      b.disabled = false;
    });
  }

  document.addEventListener("submit", function (e) {
    var form = e.target.closest("form");
    if (!form || e.defaultPrevented || form.classList.contains("cp-form")) return;
    var metode = (form.getAttribute("method") || "get").toLowerCase();
    if (metode !== "post") return;
    if (form.dataset.sedangKirim === "1") {
      e.preventDefault();
      return;
    }
    form.dataset.sedangKirim = "1";
    var btn = e.submitter || form.querySelector('button[type="submit"], button:not([type])');
    tandaiMemuat(btn);
    /* Tunda disabled ke giliran berikutnya agar name/value tombol submitter tetap terkirim. */
    var daftarBtn = form.querySelectorAll('button[type="submit"], button:not([type])');
    window.setTimeout(function () {
      if (form.dataset.sedangKirim !== "1") return;
      daftarBtn.forEach(function (b) {
        if (!b.disabled) {
          b.dataset.dinonaktifkanKirim = "1";
          b.disabled = true;
        }
      });
    }, 0);
  });

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    var tautan = e.target.closest('a[href*="segarkan=1"]');
    if (!tautan) return;
    if (tautan.classList.contains("sedang-memuat")) {
      e.preventDefault();
      return;
    }
    tandaiMemuat(tautan);
  });

  window.addEventListener("pageshow", function (event) {
    if (event.persisted || document.querySelector(".sedang-memuat")) {
      bersihkanMemuat();
    }
  });
})();
