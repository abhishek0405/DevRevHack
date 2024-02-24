class Devrev < Formula
  desc "devrev-cli"
  homepage "https://devrev.ai"
  version "0.4.5"

  on_macos do
      if Hardware::CPU.arm?
        url "https://github.com/devrev/cli/releases/download/v0.4.5/devrev_0.4.5_Darwin_arm64.tar.gz"
        sha256 "eb5da492ad1e1199d30b2706966cb6eeeca0326d7f4c19036644fca32b13b004"
        def install
          bin.install "devrev"
        end
        test do
          assert_match "devrev version v0.4.5  
gateway version 013f5f5dfb8c36c24366c2e80150c97eaf15e724" , shell_output("devrev --version")
        end
      end
      if Hardware::CPU.intel?
        url "https://github.com/devrev/cli/releases/download/v0.4.5/devrev_0.4.5_Darwin_x86_64.tar.gz"
        sha256 "70c228fc40c1f5d4eed6bc4646de6133a601b15e375169e0faad60fa0c8f68b4"
        def install
          bin.install "devrev"
        end
        test do
           assert_match "devrev version v0.4.5  
gateway version 013f5f5dfb8c36c24366c2e80150c97eaf15e724" , shell_output("devrev --version")
        end
      end
    end
    on_linux do
      if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
        url "https://github.com/devrev/cli/releases/download/v0.4.5/devrev_0.4.5_Linux_arm64.tar.gz"
        sha256 "b9ecd95b518a18b3965ef6d6eff90ba21c287e719f9e9e6b4af12ac84cf8d66c"
        def install
          bin.install "devrev"
        end
        test do
           assert_match "devrev version v0.4.5  
gateway version 013f5f5dfb8c36c24366c2e80150c97eaf15e724" , shell_output("devrev --version")
        end
      end
      if Hardware::CPU.intel?
        url "https://github.com/devrev/cli/releases/download/v0.4.5/devrev_0.4.5_Linux_x86_64.tar.gz"
        sha256 "6151dd48b50a03d0da13bce377b0172a3d0575218e9e7300b03f14c6e8f5e8b1"
        def install
          bin.install "devrev"
        end
        test do
          assert_match "devrev version v0.4.5  
gateway version 013f5f5dfb8c36c24366c2e80150c97eaf15e724" , shell_output("devrev --version")
        end
      end
    end
  end
