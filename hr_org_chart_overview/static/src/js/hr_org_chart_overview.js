odoo.define("hr_org_chart_overview.hr_org_chart_overview", function (require) {
    "use strict";

var core = require("web.core");
var AbstractAction = require("web.AbstractAction");
var QWeb = core.qweb;
var _t = core._t;

var HrOrgChartOverview = AbstractAction.extend({
    template: "HrOrgChartOverview",
    events: {
        "click .node": "_onClickNode",
        "click #print-pdf": "_onPrintPDF",
        "click #search-all": "_onKeyUpSearch",
        "click #clear-all": "_onClearAll",
        "click #zoom-in": "_onClickZoomIn",
        "click #zoom-out": "_onClickZoomOut",
        "click #toggle-pan": "_onClickTogglePan",
        "keypress .o_searchview_input_container select":"_onKeyUpSubmit",
        "change .o_searchview_input_container select" : "_onkeyOnchange",
    },

    init: function (parent) {
        this.orgChartData = {};
        this.actionManager = parent;
        console.log(this.actionManager);
        this._super.apply(this, arguments);
    },

    /**
     * @override
     */
    willStart: function () {
        var self = this;
        console.log("=======",self)
        var def = this._rpc({
            model: "hr.employee",
            method: "get_organization_data",
        },{'async': false}).then(function (res) {
            self.orgChartData = res;
        });
        return this._super.apply(this, arguments);
    },

    _getNodeTemplate: function (data) {
        return `
            <span class="image"><img src="data:image/png;base64,${data.image}"/></span>
            <div class="title">${data.name}</div>
            <div class="content">${data.title}</div>
        `;
    },

    _renderButtons: function () {
        this.$buttons = this.$(".o_cp_buttons");
        this.$buttons.prepend(`
            <button type="button" id="print-pdf" class="btn btn-primary o-kanban-button-new" accesskey="p">
                Print PDF
            </button>
            <button type="button" id="zoom-in" class="btn btn-primary o-kanban-button-new" accesskey="+">
                <i class="fa fa-plus" title="Zoom In"></i>
            </button>
            <button type="button" id="toggle-pan" class="btn o-kanban-button-new" accesskey="m">
                <i class="fa fa-arrows" title="Toggle Pan"></i>
            </button>
            <button type="button" id="zoom-out" class="btn btn-primary o-kanban-button-new" accesskey="-">
                <i class="fa fa-minus" title="Zoom Out"></i>
            </button>
        `);
    },

    _renderSearchView: function (id) {
        var self = this;
        this.$searchView = this.$(".o_cp_searchview");
        self._rpc({
            model: "hr.department",
            method: "get_department_data",
            args: [[id]],
        }).then(function (data) {
            self.$searchView.prepend(QWeb.render('orgchart-searchview', {
                widget: self,
                data: data,
            }));
        });

    },

    _renderBreadcrumb: function () {
        this.$breadcrumb = this.$(".breadcrumb");
        this.$breadcrumb.prepend(`
            <li class="breadcrumb-item active">Organizational Chart</li>
        `);
    },

    _updateControlPanel: function () {
        this._renderButtons();
        this._renderSearchView();
        this._renderBreadcrumb();
    },

    start: function () {

        this.oc = this.$("#chart-container").orgchart({
            data: this.orgChartData,
            nodeContent: "title",
            nodeTemplate: this._getNodeTemplate,
            exportFilename: "MyOrgChart",
        });

        this._updateControlPanel();

        return this._super.apply(this, arguments);
    },
    _clearFilterResults: function () {
        this.$(".orgchart")
            .removeClass("noncollapsable")
            .find(".node")
            .removeClass("matched retained")
            .end()
            .find(".hidden")
            .removeClass("hidden")
            .end()
            .find(".slide-up, .slide-left, .slide-right")
            .removeClass("slide-up slide-right slide-left");
    },

    _openEmployeeFormView: function (id) {
        var self = this;
        // Go to the employee form view
        self._rpc({
            model: "hr.employee",
            method: "get_formview_action",
            args: [[id]],
        }).then(function (action) {
            self.trigger_up("do_action", {action: action});
        });
    },

    _onClickNode: function (ev) {
        ev.preventDefault();
        // this._openEmployeeFormView(parseInt(ev.currentTarget.id));
    },

    _onPrintPDF: function (ev) {
        ev.preventDefault();
        this.oc.export(this.oc.exportFilename, "pdf");
    },

    _onClickZoomIn: function (ev) {
        ev.preventDefault();
        this.oc.setChartScale(this.oc.$chart, 1.1);
    },

    _onClickZoomOut: function (ev) {
        ev.preventDefault();
        this.oc.setChartScale(this.oc.$chart, 0.9);
    },

    _onClickTogglePan: function (ev) {
        ev.preventDefault();
        var update_pan_to = !this.oc.options.pan;
        this.oc.options.pan = update_pan_to;
        this.oc.setOptions("pan", update_pan_to);
        if (update_pan_to === true) {
            $("#toggle-pan").addClass("btn-primary");
        } else {
            $("#toggle-pan").removeClass("btn-primary");
        }
    },

    _onPrintPNG: function (ev) {
        ev.preventDefault();
        this.oc.export(this.oc.exportFilename);
    },

     _onClearAll: function (ev) {
     var chart_container = self.$("#chart-container")
        chart_container.find('.orgchart').remove()
        $('.o_searchview_input_container input, .o_searchview_input_container select').val('')
    },

    _onKeyUpSubmit: function (ev){
     ev.preventDefault();
        if(ev.which && ev.currentTarget.value != ''){
            $('#search-all').trigger('click')
        }
    },

    _onkeyOnchange: function (ev){
        var self = this;
        var searchbar_names = ["group", "departments", "sections"];
        var currentTarget = $(ev.currentTarget)
        var searchbar_name = currentTarget.attr('name')
        if (searchbar_names.indexOf(searchbar_name)!=-1){
            var nextElementId = searchbar_name == 'group' && 'departments' || false
            nextElementId = !nextElementId && searchbar_name == 'departments' && 'sections' || nextElementId
            nextElementId = !nextElementId && searchbar_name == 'sections' && 'subsections' || nextElementId
            nextElementId = $('select[name="'+nextElementId+'"]')
            nextElementId.find('option').remove()
            if (nextElementId.attr('name')==='departments'){
                nextElementId.append($('<option value="">Select Departments</option>'))
            }
            if (nextElementId.attr('name')==='sections'){
                nextElementId.append($('<option value="">Select Sections</option>'))
            }
            if  (nextElementId.attr('name')==='subsections'){
                nextElementId.append($('<option value="" >Select Subsections</option>'))
            }
            var value_id =  currentTarget.val()
            var dict_search={searchbar_value:value_id,searchbar_name:searchbar_name}
            self._rpc({
                model: "hr.department",
                method: "get_department_from_searchbar",
                args: ["",dict_search],
            }).then(function (data) {
                _.each(data, function(value,key) {
                    nextElementId.append(
                        $('<option value=' + key + '>' + value + '</option>')
                    )
                });
            });
        }
    },

    _onKeyUpSearch: function (ev) {
        // var value = ev.target.value.toLowerCase();
        var self = this
        var value1 = $("#key-word1").val();
        var value2 = $("#key-word2").val();
        var value3 = $("#key-word3").val();
        var value4 = $("#key-word4").val();
        var value5 = $("#key-word5").val();
        var value6 = $("#key-word6").val();
        var value7 = $("#key-word7").val();
        var value8 = $("#key-word8").val();
        if (value1.length === 0 && value2.length === 0 && value3.length === 0 && value4.length === 0 && value5.length === 0 && value6.length === 0 && value7.length === 0  && value8.length === 0) {
            var chart_container = self.$("#chart-container")
            chart_container.find('.orgchart').remove()
        } else {
        var def = this._rpc({
            model: "hr.employee",
            method: "search_department_result",
            args: ["",value1,value2,value3,value4,value5,value6,value7,value8],
        }).then(function (result) {
        var chart_container = self.$("#chart-container")
        chart_container.find('.orgchart').remove()
         self.oc = chart_container.orgchart({
            data: result,
            nodeContent: "title",
            nodeTemplate: self._getNodeTemplate,
            exportFilename: "MyOrgChart",
        });

        });
        }
    },
});

core.action_registry.add("hr_org_chart_overview", HrOrgChartOverview);
return {
    HrOrgChartOverview: HrOrgChartOverview,
}
});
