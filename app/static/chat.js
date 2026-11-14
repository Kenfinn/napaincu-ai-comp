/* Ask FEAF floating chat panel & multi-turn conversation script (C4).
   Vanilla JS, no frameworks, strict textContent rendering. */
(function () {
  "use strict";

  var KUNCI_SIMPAN = "feaf_chat";
  var KUNCI_BUKA = "feaf_chat_buka";
  var MAKS_PESAN = 12;

  function muatRiwayat() {
    try {
      var mentah = window.sessionStorage.getItem(KUNCI_SIMPAN);
      if (!mentah) return [];
      var daftar = JSON.parse(mentah);
      return Array.isArray(daftar) ? daftar.slice(-MAKS_PESAN) : [];
    } catch (_e) {
      return [];
    }
  }

  function simpanRiwayat(daftar) {
    try {
      var potong = (daftar || []).slice(-MAKS_PESAN);
      window.sessionStorage.setItem(KUNCI_SIMPAN, JSON.stringify(potong));
    } catch (_e) {
      /* ignore quota/storage errors */
    }
  }

  function formatTautanLabel(tplBuka, jalur) {
    if (!tplBuka) return jalur + " \u2192";
    return tplBuka.replace("{jalur}", jalur);
  }

  function buatElemenPesan(item, label) {
    var bungkus = document.createElement("div");
    var peran = item.peran === "user" ? "user" : "asisten";
    bungkus.className = "cp-pesan cp-pesan-" + peran;

    var teks = document.createElement("div");
    teks.className = "cp-pesan-teks";
    teks.textContent = item.teks || "";
    bungkus.appendChild(teks);

    if (peran === "asisten") {
      if (item.jalur === "template_setelah_tolak" && label.catatanTolak) {
        var cat = document.createElement("div");
        cat.className = "cp-catatan-tolak";
        cat.textContent = label.catatanTolak;
        bungkus.appendChild(cat);
      }

      if (Array.isArray(item.tautan) && item.tautan.length > 0) {
        var barisTautan = document.createElement("div");
        barisTautan.className = "cp-tautan-baris";
        for (var i = 0; i < item.tautan.length; i++) {
          var t = String(item.tautan[i] || "");
          if (t.charAt(0) !== "/") continue;
          var a = document.createElement("a");
          a.className = "cp-pil-tautan";
          a.href = t;
          a.textContent = formatTautanLabel(label.bukaHalaman, t);
          barisTautan.appendChild(a);
        }
        if (barisTautan.childNodes.length > 0) {
          bungkus.appendChild(barisTautan);
        }
      }

      if ((Array.isArray(item.sumber) && item.sumber.length > 0) || item.id) {
        var meta = document.createElement("div");
        meta.className = "cp-meta-baris";

        var blokSumber = document.createElement("span");
        if (Array.isArray(item.sumber) && item.sumber.length > 0) {
          blokSumber.textContent = (label.sumber || "Sources:") + " ";
          for (var j = 0; j < item.sumber.length; j++) {
            if (j > 0) {
              blokSumber.appendChild(document.createTextNode(" \u00b7 "));
            }
            var s = String(item.sumber[j] || "");
            var bag = s.split(" ")[0];
            if (bag.indexOf("http") === 0 || bag.charAt(0) === "/") {
              var tautS = document.createElement("a");
              tautS.href = bag;
              tautS.textContent = s;
              blokSumber.appendChild(tautS);
            } else {
              blokSumber.appendChild(document.createTextNode(s));
            }
          }
        }
        meta.appendChild(blokSumber);

        if (item.id) {
          var tautJejak = document.createElement("a");
          tautJejak.href = "/api/ask/traces/" + encodeURIComponent(item.id);
          tautJejak.target = "_blank";
          tautJejak.rel = "noopener";
          tautJejak.textContent = (label.jejak || "Trace") + " #" + String(item.id).slice(-6);
          meta.appendChild(tautJejak);
        }
        bungkus.appendChild(meta);
      }
    }
    return bungkus;
  }

  function pasangWadahChat(akar, modePanel) {
    if (!akar) return;
    var ds = akar.dataset;
    var konteks = {
      halaman: ds.halaman || "",
      kode: ds.kode || "",
      id: ds.id || ""
    };
    var bahasa = ds.bahasa || "en";
    var label = {
      kosong: ds.teksKosong || "",
      memuat: ds.teksMemuat || "...",
      galatJaringan: ds.teksGalatJaringan || "Network error.",
      galatAkses: ds.teksGalatAkses || "Access code required.",
      sumber: ds.teksSumber || "Sources:",
      bukaHalaman: ds.teksBukaHalaman || "Open {jalur} \u2192",
      jejak: ds.teksJejak || "Trace",
      catatanTolak: ds.teksCatatanTolak || ""
    };

    var elDisclaimer = akar.querySelector(".cp-disclaimer");
    if (elDisclaimer && ds.d1 !== undefined) {
      elDisclaimer.textContent = (ds.d1 || "") + (ds.d2 || "");
    }

    var elDaftar = akar.querySelector(".cp-daftar");
    var elForm = akar.querySelector(".cp-form");
    var elInput = akar.querySelector(".cp-input");
    var elKirim = akar.querySelector(".cp-kirim");
    var elRecap = akar.querySelector(".cp-aksi-recap");
    var elBaru = akar.querySelector(".cp-aksi-baru");
    var chips = akar.querySelectorAll(".cp-chip");

    function renderDaftar() {
      if (!elDaftar) return;
      while (elDaftar.firstChild) {
        elDaftar.removeChild(elDaftar.firstChild);
      }
      var riwayat = muatRiwayat();
      if (riwayat.length === 0) {
        var kosong = document.createElement("div");
        kosong.className = "cp-kosong";
        kosong.textContent = label.kosong;
        elDaftar.appendChild(kosong);
        return;
      }
      for (var i = 0; i < riwayat.length; i++) {
        elDaftar.appendChild(buatElemenPesan(riwayat[i], label));
      }
      elDaftar.scrollTop = elDaftar.scrollHeight;
    }

    function kirimPertanyaan(teksPertanyaan, jenisKhusus) {
      var q = String(teksPertanyaan || "").trim();
      if (!q && jenisKhusus !== "recap") return;
      var riwayatLama = muatRiwayat();
      var riwayatKirim = riwayatLama.map(function (it) {
        return {
          peran: it.peran,
          teks: it.teks,
          id: it.id || "",
          tanda: it.tanda || ""
        };
      });

      var teksTampil = jenisKhusus === "recap" && !q ? (elRecap ? elRecap.textContent : "Recap") : q;
      var daftarSekarang = riwayatLama.slice();
      if (jenisKhusus !== "recap") {
        daftarSekarang.push({ peran: "user", teks: teksTampil });
        simpanRiwayat(daftarSekarang);
      }
      renderDaftar();

      var elMemuat = document.createElement("div");
      elMemuat.className = "cp-pesan cp-pesan-asisten";
      var teksMemuat = document.createElement("div");
      teksMemuat.className = "cp-pesan-teks";
      teksMemuat.textContent = "\u2026 " + label.memuat;
      elMemuat.appendChild(teksMemuat);
      if (elDaftar) {
        elDaftar.appendChild(elMemuat);
        elDaftar.scrollTop = elDaftar.scrollHeight;
      }

      if (elInput && jenisKhusus !== "recap") {
        elInput.value = "";
      }
      if (elKirim) elKirim.disabled = true;

      var payload = {
        pertanyaan: teksTampil,
        bahasa: bahasa,
        riwayat: riwayatKirim,
        konteks: konteks
      };
      if (jenisKhusus) {
        payload.jenis = jenisKhusus;
      }

      window.fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      })
        .then(function (resp) {
          if (resp.status === 401) {
            throw { kode: 401 };
          }
          if (!resp.ok) {
            throw { kode: resp.status };
          }
          return resp.json();
        })
        .then(function (data) {
          if (elKirim) elKirim.disabled = false;
          var itemAsisten = {
            peran: "asisten",
            teks: data.jawaban || "",
            id: data.id || "",
            tanda: data.tanda || "",
            sumber: data.sumber || [],
            tautan: data.tautan || [],
            jalur: data.jalur || ""
          };
          if (jenisKhusus === "recap") {
            if (elMemuat.parentNode) {
              elMemuat.parentNode.removeChild(elMemuat);
            }
            if (elDaftar) {
              elDaftar.appendChild(buatElemenPesan({ peran: "user", teks: teksTampil }, label));
              elDaftar.appendChild(buatElemenPesan(itemAsisten, label));
              elDaftar.scrollTop = elDaftar.scrollHeight;
            }
          } else {
            daftarSekarang.push(itemAsisten);
            simpanRiwayat(daftarSekarang);
            renderDaftar();
          }
        })
        .catch(function (err) {
          if (elKirim) elKirim.disabled = false;
          if (elMemuat.parentNode) {
            elMemuat.parentNode.removeChild(elMemuat);
          }
          var pesanGalat = err && err.kode === 401 ? label.galatAkses : label.galatJaringan;
          if (elDaftar) {
            elDaftar.appendChild(buatElemenPesan({ peran: "asisten", teks: pesanGalat }, label));
            elDaftar.scrollTop = elDaftar.scrollHeight;
          }
        });
    }

    if (elForm) {
      elForm.addEventListener("submit", function (ev) {
        ev.preventDefault();
        if (elInput) {
          kirimPertanyaan(elInput.value, null);
        }
      });
    }

    if (elInput) {
      elInput.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
          ev.preventDefault();
          kirimPertanyaan(elInput.value, null);
        }
      });
    }

    if (elRecap) {
      elRecap.addEventListener("click", function (ev) {
        ev.preventDefault();
        kirimPertanyaan(elRecap.getAttribute("data-q") || "Recap", "recap");
      });
    }

    if (elBaru) {
      elBaru.addEventListener("click", function (ev) {
        ev.preventDefault();
        simpanRiwayat([]);
        renderDaftar();
        if (elInput) elInput.focus();
      });
    }

    for (var c = 0; c < chips.length; c++) {
      chips[c].addEventListener("click", function (ev) {
        ev.preventDefault();
        var q = this.getAttribute("data-q") || this.textContent;
        kirimPertanyaan(q, null);
      });
    }

    renderDaftar();

    if (modePanel) {
      var fab = document.getElementById("cp-fab");
      var panel = document.getElementById("cp-panel");
      var latar = document.getElementById("cp-latar");
      var tutup = document.getElementById("cp-tutup");

      function bukaPanel(fokusInput) {
        if (!panel) return;
        panel.hidden = false;
        if (latar) latar.hidden = false;
        if (fab) fab.setAttribute("aria-expanded", "true");
        try {
          window.sessionStorage.setItem(KUNCI_BUKA, "1");
        } catch (_e) {}
        renderDaftar();
        if (fokusInput && elInput) {
          elInput.focus();
        }
      }

      function tutupPanel(fokusFab) {
        if (!panel) return;
        panel.hidden = true;
        if (latar) latar.hidden = true;
        if (fab) fab.setAttribute("aria-expanded", "false");
        try {
          window.sessionStorage.removeItem(KUNCI_BUKA);
        } catch (_e) {}
        if (fokusFab && fab) {
          fab.focus();
        }
      }

      if (fab) {
        fab.addEventListener("click", function (ev) {
          ev.preventDefault();
          if (panel && !panel.hidden) {
            tutupPanel(true);
          } else {
            bukaPanel(true);
          }
        });
      }
      if (tutup) {
        tutup.addEventListener("click", function (ev) {
          ev.preventDefault();
          tutupPanel(true);
        });
      }
      if (latar) {
        latar.addEventListener("click", function () {
          tutupPanel(true);
        });
      }
      document.addEventListener("keydown", function (ev) {
        if (ev.key === "Escape" && panel && !panel.hidden) {
          ev.preventDefault();
          tutupPanel(true);
        }
      });

      try {
        if (window.sessionStorage.getItem(KUNCI_BUKA) === "1") {
          bukaPanel(false);
        }
      } catch (_e) {}
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    pasangWadahChat(document.getElementById("cp-akar"), true);
    pasangWadahChat(document.getElementById("cp-halaman-akar"), false);
  });
})();
