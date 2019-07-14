module.exports = {
  title: "MechWolf",
  description: "Continuous flow process automation made easy",
  themeConfig: {
    logo: "/head10x.png",
    lastUpdated: "Last Updated", // string | boolean
    repo: "Benjamin-Lee/mechwolf",
    editLinks: true,
    sidebar: {
      "/api/": [
        {
          title: "Core",
          collapsable: false,
          children: [
            "/api/core/apparatus",
            "/api/core/protocol",
            "/api/core/experiment"
          ]
        },
        {
          title: "Component Standard Library",
          collapsable: false,
          children: [
            "/api/components/stdlib/pump",
            "/api/components/stdlib/valve",
            "/api/components/stdlib/mixer"
          ]
        },
        {
          title: "Contributed Component Library",
          collapsable: false,
          children: [
            "/api/components/stdlib/pump",
            "/api/components/stdlib/valve",
            "/api/components/stdlib/mixer"
          ]
        }
      ],
      "/": [
        "/intro",
        {
          title: "About",
          collapsable: false,
          children: [
            "/about/faq",
            "/about/support",
            "/about/why",
            "about/license"
          ]
        },
        {
          title: "Guide",
          collapsable: false,
          children: [
            "/guide/gentle_intro",
            "/guide/installation",
            "/guide/getting_started",
            "/guide/new_components"
          ]
        },
        "/api/"
      ]
    }
  }
}
