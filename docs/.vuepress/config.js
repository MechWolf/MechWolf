module.exports = {
  title: "MechWolf",
  description: "Continuous flow process automation made easy",
  themeConfig: {
    logo: "/head10x.png",
    lastUpdated: "Last Updated", // string | boolean
    repo: "Benjamin-Lee/mechwolf",
    editLinks: true,
    sidebar: [
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
      {
        title: "API Reference",
        collapsable: false,
        children: [
          "/api/mechwolf",
          "/api/stdlib_components"
        ]
      }
    ]
  }
};
